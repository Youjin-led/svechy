import shutil
from pathlib import Path

from multi_agent_site import ROOT, ToolRegistry


def status(name: str, value: str | None) -> None:
    marker = "OK" if value else "MISSING"
    print(f"[{marker}] {name}: {value or 'not found'}")


def main() -> None:
    tools = ToolRegistry()
    status("Blender", tools.blender_path)
    status("External 3D artist folder", str(tools.external_artist_dir) if tools.external_artist_dir else None)
    status("External 3D artist MCP", str(tools.external_artist_mcp) if tools.external_artist_mcp else None)
    status("External 3D artist GLB", str(tools.external_artist_model) if tools.external_artist_model else None)
    status("Node.js", shutil.which("node"))
    status("npm", shutil.which("npm") or shutil.which("npm.cmd"))
    status("Puppeteer", str(ROOT / "node_modules" / "puppeteer") if (ROOT / "node_modules" / "puppeteer").exists() else None)
    status("Three.js", str(ROOT / "node_modules" / "three") if (ROOT / "node_modules" / "three").exists() else None)
    print(f"[INFO] Project root: {Path(ROOT)}")


if __name__ == "__main__":
    main()
