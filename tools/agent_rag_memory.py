#!/usr/bin/env python3
"""
agent_rag_memory.py — RAG-память агента на ChromaDB + sentence-transformers.

Команды:
  python tools/agent_rag_memory.py add <key> <value>   — добавить запись
  python tools/agent_rag_memory.py search <query>       — семантический поиск
  python tools/agent_rag_memory.py list                  — все записи
  python tools/agent_rag_memory.py delete <key>          — удалить по ключу
  python tools/agent_rag_memory.py rebuild               — перестроить из SQLite памяти
"""

import sys
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent.parent
CHROMA_DIR = ROOT / ".chroma_db"
SQLITE_PATH = ROOT / ".agent_memory.sqlite3"

# Lazy imports
_chroma_client = None
_encoder = None

def get_encoder():
    global _encoder
    if _encoder is None:
        from sentence_transformers import SentenceTransformer
        _encoder = SentenceTransformer("all-MiniLM-L6-v2")
    return _encoder

def get_chroma():
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _chroma_client

def get_or_create_collection(name="agent_memory"):
    client = get_chroma()
    try:
        return client.get_collection(name)
    except:
        return client.create_collection(name)

def embed(text: str):
    return get_encoder().encode(text).tolist()

def cmd_add(key: str, value: str):
    collection = get_or_create_collection()
    existing = collection.get(ids=[key])
    if existing["ids"]:
        collection.update(ids=[key], embeddings=[embed(value)], metadatas=[{"key": key}], documents=[value])
    else:
        collection.add(ids=[key], embeddings=[embed(value)], metadatas=[{"key": key}], documents=[value])
    print(f"[OK] Added/updated: {key}")

def cmd_search(query: str, n_results: int = 5):
    collection = get_or_create_collection()
    results = collection.query(query_embeddings=[embed(query)], n_results=n_results)
    if not results["ids"][0]:
        print("[INFO] No results found.")
        return
    for i, (doc_id, doc, meta, dist) in enumerate(zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        print(f"\n--- Result {i+1} (distance: {dist:.4f}) ---")
        print(f"  Key: {doc_id}")
        print(f"  Value: {doc[:300]}{'...' if len(doc) > 300 else ''}")

def cmd_list():
    collection = get_or_create_collection()
    all_data = collection.get()
    if not all_data["ids"]:
        print("[INFO] Memory is empty.")
        return
    print(f"\nTotal entries: {len(all_data['ids'])}")
    for doc_id, doc in zip(all_data["ids"], all_data["documents"]):
        print(f"  [{doc_id}]: {doc[:80]}{'...' if len(doc) > 80 else ''}")

def cmd_delete(key: str):
    collection = get_or_create_collection()
    collection.delete(ids=[key])
    print(f"[OK] Deleted: {key}")

def cmd_rebuild():
    """Перестроить ChromaDB из SQLite памяти."""
    if not SQLITE_PATH.exists():
        print("[ERROR] SQLite database not found.")
        return
    
    conn = sqlite3.connect(str(SQLITE_PATH))
    cursor = conn.cursor()
    
    # Проверяем структуру
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    entries = []
    
    if "memories" in tables:
        cursor.execute("SELECT id, content FROM memories")
        entries = [(str(row[0]), row[1]) for row in cursor.fetchall()]
    elif "memory" in tables:
        cursor.execute("SELECT key, value FROM memory")
        entries = cursor.fetchall()
    elif "episodes" in tables:
        cursor.execute("SELECT id, task FROM episodes")
        entries = [(str(row[0]), row[1]) for row in cursor.fetchall()]
    
    conn.close()
    
    if not entries:
        print("[INFO] No entries to rebuild from.")
        return
    
    collection = get_or_create_collection()
    
    # Очищаем коллекцию
    try:
        client = get_chroma()
        client.delete_collection("agent_memory")
    except:
        pass
    
    collection = get_or_create_collection()
    
    keys = [e[0] for e in entries]
    values = [e[1] for e in entries]
    embeddings = [embed(v) for v in values]
    metadatas = [{"key": k} for k in keys]
    
    # Добавляем батчами по 100
    batch_size = 100
    for i in range(0, len(keys), batch_size):
        batch_end = min(i + batch_size, len(keys))
        collection.add(
            ids=keys[i:batch_end],
            embeddings=embeddings[i:batch_end],
            metadatas=metadatas[i:batch_end],
            documents=values[i:batch_end]
        )
    
    print(f"[OK] Rebuilt ChromaDB with {len(keys)} entries from SQLite.")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == "add" and len(sys.argv) >= 4:
        cmd_add(sys.argv[2], " ".join(sys.argv[3:]))
    elif command == "search" and len(sys.argv) >= 3:
        cmd_search(" ".join(sys.argv[2:]))
    elif command == "list":
        cmd_list()
    elif command == "delete" and len(sys.argv) >= 3:
        cmd_delete(sys.argv[2])
    elif command == "rebuild":
        cmd_rebuild()
    else:
        print(f"[ERROR] Unknown command or missing arguments: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()
