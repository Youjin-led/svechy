import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / ".agent_memory.sqlite3"
MARKDOWN_MEMORY = ROOT / "AGENT_MEMORY.md"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def ensure_column(connection: sqlite3.Connection, name: str, definition: str) -> None:
    columns = {row[1] for row in connection.execute("PRAGMA table_info(memories)").fetchall()}
    if name not in columns:
        connection.execute(f"ALTER TABLE memories ADD COLUMN {name} {definition}")


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            tags TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL,
            importance INTEGER NOT NULL DEFAULT 3,
            access_count INTEGER NOT NULL DEFAULT 0,
            last_accessed TEXT,
            archived INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    ensure_column(connection, "importance", "INTEGER NOT NULL DEFAULT 3")
    ensure_column(connection, "access_count", "INTEGER NOT NULL DEFAULT 0")
    ensure_column(connection, "last_accessed", "TEXT")
    ensure_column(connection, "archived", "INTEGER NOT NULL DEFAULT 0")
    connection.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
        USING fts5(content, tags, content='memories', content_rowid='id')
        """
    )
    return connection


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sync_fts(connection: sqlite3.Connection, memory_id: int, content: str, tags: str) -> None:
    connection.execute(
        "INSERT INTO memories_fts(rowid, content, tags) VALUES (?, ?, ?)",
        (memory_id, content, tags),
    )


def add_memory(args: argparse.Namespace) -> None:
    content = " ".join(args.content).strip()
    tags = ",".join(args.tag or [])
    if not content:
        raise SystemExit("Memory content is empty.")

    with connect() as connection:
        cursor = connection.execute(
            "INSERT INTO memories(created_at, tags, content, importance) VALUES (?, ?, ?, ?)",
            (now_iso(), tags, content, args.importance),
        )
        sync_fts(connection, cursor.lastrowid, content, tags)
        print(f"[OK] Added memory #{cursor.lastrowid}")


def search_memories(args: argparse.Namespace) -> None:
    query = " ".join(args.query).strip()
    if not query:
        raise SystemExit("Search query is empty.")

    with connect() as connection:
        rows = connection.execute(
            """
            SELECT m.id, m.created_at, m.tags, m.content
            FROM memories_fts f
            JOIN memories m ON m.id = f.rowid
            WHERE memories_fts MATCH ?
            AND m.archived = 0
            ORDER BY rank
            LIMIT ?
            """,
            (query, args.limit),
        ).fetchall()

    if not rows:
        print("[INFO] No matching memories found.")
        return

    for memory_id, created_at, tags, content in rows:
        mark_accessed(memory_id)
        tag_text = f" tags={tags}" if tags else ""
        print(f"#{memory_id} {created_at}{tag_text}\n{content}\n")


def list_memories(args: argparse.Namespace) -> None:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT id, created_at, tags, content
            FROM memories
            WHERE archived = 0
            ORDER BY id DESC
            LIMIT ?
            """,
            (args.limit,),
        ).fetchall()

    if not rows:
        print("[INFO] Memory database is empty.")
        return

    for memory_id, created_at, tags, content in rows:
        tag_text = f" tags={tags}" if tags else ""
        print(f"#{memory_id} {created_at}{tag_text}\n{content}\n")


def import_markdown(_: argparse.Namespace) -> None:
    if not MARKDOWN_MEMORY.exists():
        raise SystemExit(f"{MARKDOWN_MEMORY.name} does not exist.")

    lines = MARKDOWN_MEMORY.read_text(encoding="utf-8").splitlines()
    notes = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            notes.append(stripped[2:])

    if not notes:
        print("[INFO] No markdown memory bullet notes found.")
        return

    with connect() as connection:
        added = 0
        for note in notes:
            exists = connection.execute(
                "SELECT 1 FROM memories WHERE content = ? LIMIT 1",
                (note,),
            ).fetchone()
            if exists:
                continue
            cursor = connection.execute(
                "INSERT INTO memories(created_at, tags, content, importance) VALUES (?, ?, ?, ?)",
                (now_iso(), "imported,markdown", note, 3),
            )
            sync_fts(connection, cursor.lastrowid, note, "imported,markdown")
            added += 1

    print(f"[OK] Imported {added} markdown memories into {DB_PATH.name}")


def stats(_: argparse.Namespace) -> None:
    with connect() as connection:
        count = connection.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        archived = connection.execute("SELECT COUNT(*) FROM memories WHERE archived = 1").fetchone()[0]
        tags = connection.execute(
            "SELECT tags, COUNT(*) FROM memories WHERE tags != '' GROUP BY tags ORDER BY COUNT(*) DESC"
        ).fetchall()

    print(f"[INFO] Database: {DB_PATH}")
    print(f"[INFO] Memories: {count}")
    print(f"[INFO] Archived: {archived}")
    if tags:
        print("[INFO] Tag groups:")
        for tag, amount in tags:
            print(f"- {tag}: {amount}")


def mark_accessed(memory_id: int) -> None:
    with connect() as connection:
        connection.execute(
            """
            UPDATE memories
            SET access_count = access_count + 1, last_accessed = ?
            WHERE id = ?
            """,
            (now_iso(), memory_id),
        )


def touch_memory(args: argparse.Namespace) -> None:
    with connect() as connection:
        row = connection.execute(
            "SELECT id, content FROM memories WHERE id = ?",
            (args.id,),
        ).fetchone()
        if not row:
            raise SystemExit(f"Memory #{args.id} not found.")
        connection.execute(
            """
            UPDATE memories
            SET access_count = access_count + 1,
                last_accessed = ?,
                importance = MIN(5, importance + ?)
            WHERE id = ?
            """,
            (now_iso(), args.boost, args.id),
        )
    print(f"[OK] Touched memory #{args.id}")


def prune_candidates(args: argparse.Namespace) -> None:
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT id, created_at, tags, importance, access_count, last_accessed, content
            FROM memories
            WHERE archived = 0
            ORDER BY importance ASC, access_count ASC, id ASC
            LIMIT ?
            """,
            (args.limit,),
        ).fetchall()

    if not rows:
        print("[INFO] No prune candidates.")
        return
    for memory_id, created_at, tags, importance, access_count, last_accessed, content in rows:
        print(
            f"#{memory_id} importance={importance} access_count={access_count} "
            f"created={created_at} last_accessed={last_accessed or '-'} tags={tags or '-'}\n{content}\n"
        )


def archive_memory(args: argparse.Namespace) -> None:
    with connect() as connection:
        cursor = connection.execute(
            "UPDATE memories SET archived = 1 WHERE id = ?",
            (args.id,),
        )
    if cursor.rowcount == 0:
        raise SystemExit(f"Memory #{args.id} not found.")
    print(f"[OK] Archived memory #{args.id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local SQLite memory for the project agent.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="Add a memory.")
    add.add_argument("content", nargs="+")
    add.add_argument("--tag", action="append", help="Attach a tag. Can be repeated.")
    add.add_argument("--importance", type=int, default=3, choices=range(1, 6))
    add.set_defaults(func=add_memory)

    search = subparsers.add_parser("search", help="Search memories using SQLite FTS.")
    search.add_argument("query", nargs="+")
    search.add_argument("--limit", type=int, default=10)
    search.set_defaults(func=search_memories)

    list_command = subparsers.add_parser("list", help="List latest memories.")
    list_command.add_argument("--limit", type=int, default=20)
    list_command.set_defaults(func=list_memories)

    imported = subparsers.add_parser("import-md", help="Import bullet notes from AGENT_MEMORY.md.")
    imported.set_defaults(func=import_markdown)

    stat_command = subparsers.add_parser("stats", help="Show database stats.")
    stat_command.set_defaults(func=stats)

    touch = subparsers.add_parser("touch", help="Mark a memory as useful.")
    touch.add_argument("id", type=int)
    touch.add_argument("--boost", type=int, default=1, choices=range(0, 3))
    touch.set_defaults(func=touch_memory)

    prune = subparsers.add_parser("prune-candidates", help="Show low-value memory candidates.")
    prune.add_argument("--limit", type=int, default=10)
    prune.set_defaults(func=prune_candidates)

    archive = subparsers.add_parser("archive", help="Archive a memory without deleting it.")
    archive.add_argument("id", type=int)
    archive.set_defaults(func=archive_memory)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
