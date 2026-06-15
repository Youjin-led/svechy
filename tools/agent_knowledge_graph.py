#!/usr/bin/env python3
"""
agent_knowledge_graph.py — Граф знаний проекта.

Анализирует файлы проекта и строит граф зависимостей:
  - HTML файлы → CSS, JS
  - JS файлы → зависимости (require/import)
  - Python файлы → импорты
  - Файлы → инструменты (tools/)
  - Решения → файлы

Команды:
  python tools/agent_knowledge_graph.py build     — построить граф
  python tools/agent_knowledge_graph.py search <q> — поиск по графу
  python tools/agent_knowledge_graph.py stats      — статистика графа
  python tools/agent_knowledge_graph.py impact <f> — "что сломается если изменить X"
"""

import sys
import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent

class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}  # id -> {type, name, path}
        self.edges = []  # [(from, to, relation)]
        self.graph_file = ROOT / "data" / "knowledge_graph.json"
    
    def add_node(self, node_id: str, node_type: str, name: str, path: str = ""):
        self.nodes[node_id] = {"type": node_type, "name": name, "path": path}
    
    def add_edge(self, from_id: str, to_id: str, relation: str):
        self.edges.append({"from": from_id, "to": to_id, "relation": relation})
    
    def build(self):
        print("[GRAPH] Building knowledge graph...")
        
        # 1. HTML файлы
        for f in ROOT.glob("*.html"):
            node_id = f"html:{f.name}"
            self.add_node(node_id, "html", f.name, str(f.relative_to(ROOT)))
            content = f.read_text(encoding="utf-8", errors="ignore")
            
            # Связи с CSS
            for css_match in re.finditer(r'<link[^>]*href="([^"]+\.css)"', content):
                css_file = css_match.group(1).split("/")[-1]
                self.add_node(f"css:{css_file}", "css", css_file)
                self.add_edge(node_id, f"css:{css_file}", "uses_styles")
            
            # Связи с JS
            for js_match in re.finditer(r'<script[^>]*src="([^"]+\.js)"', content):
                js_file = js_match.group(1).split("/")[-1]
                self.add_node(f"js:{js_file}", "js", js_file)
                self.add_edge(node_id, f"js:{js_file}", "uses_script")
        
        # 2. Python файлы
        for f in ROOT.rglob("*.py"):
            if ".uv-cache" in str(f) or "node_modules" in str(f):
                continue
            node_id = f"py:{f.name}"
            self.add_node(node_id, "python", f.name, str(f.relative_to(ROOT)))
            content = f.read_text(encoding="utf-8", errors="ignore")
            
            for imp in re.finditer(r'^(?:from|import)\s+(\S+)', content, re.MULTILINE):
                dep = imp.group(1).split(".")[0]
                self.add_edge(node_id, f"py:{dep}.py", "imports")
        
        # 3. JS файлы
        for f in ROOT.rglob("*.js"):
            if "node_modules" in str(f):
                continue
            node_id = f"js:{f.name}"
            self.add_node(node_id, "javascript", f.name, str(f.relative_to(ROOT)))
            content = f.read_text(encoding="utf-8", errors="ignore")
            
            for req in re.finditer(r'(?:require|import)\s*\(?\s*["\']([^"\']+)', content):
                dep = req.group(1).split("/")[-1]
                self.add_edge(node_id, f"js:{dep}", "requires")
        
        # 4. Инструменты (tools/)
        tools_dir = ROOT / "tools"
        if tools_dir.exists():
            for f in tools_dir.iterdir():
                if f.suffix in [".py", ".js"]:
                    node_id = f"tool:{f.name}"
                    self.add_node(node_id, "tool", f.name, str(f.relative_to(ROOT)))
        
        # Сохраняем
        data = {
            "nodes": self.nodes,
            "edges": self.edges,
            "stats": self.get_stats()
        }
        
        self.graph_file.parent.mkdir(exist_ok=True)
        self.graph_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        
        print(f"[GRAPH] Built: {len(self.nodes)} nodes, {len(self.edges)} edges")
        print(f"[GRAPH] Saved to: data/knowledge_graph.json")
        
        return data
    
    def get_stats(self):
        types = defaultdict(int)
        for node in self.nodes.values():
            types[node["type"]] += 1
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "by_type": dict(types),
        }
    
    def load(self):
        if self.graph_file.exists():
            data = json.loads(self.graph_file.read_text())
            self.nodes = data["nodes"]
            self.edges = data["edges"]
            return True
        return False
    
    def search(self, query: str):
        if not self.load():
            self.build()
        
        query_lower = query.lower()
        results = []
        
        for node_id, node in self.nodes.items():
            if query_lower in node_id.lower() or query_lower in node["name"].lower():
                results.append(node)
        
        print(f"\n[GRAPH] Search results for '{query}':")
        for r in results[:10]:
            print(f"  [{r['type']}] {r['name']} ({r.get('path', '')})")
        
        # Показываем связи
        print(f"\n  Connections:")
        for edge in self.edges:
            if any(query_lower in edge["from"].lower() or query_lower in edge["to"].lower() for r in results):
                print(f"    {edge['from']} --[{edge['relation']}]--> {edge['to']}")
        
        return results
    
    def impact(self, filename: str):
        """Что сломается если изменить файл."""
        if not self.load():
            self.build()
        
        print(f"\n[GRAPH] Impact analysis for: {filename}")
        print("=" * 50)
        
        # Ищем все связи с этим файлом
        affected = []
        for edge in self.edges:
            if filename in edge["from"] or filename in edge["to"]:
                affected.append(edge)
        
        if not affected:
            print("  No dependencies found (file may be isolated).")
            return
        
        print(f"\n  Direct dependencies ({len(affected)}):")
        for edge in affected:
            if filename in edge["from"]:
                print(f"    ❌ {edge['from']} --[{edge['relation']}]--> {edge['to']}")
            else:
                print(f"    ❌ {edge['from']} --[{edge['relation']}]--> {edge['to']}")
        
        # Рекурсивно ищем косвенные зависимости
        indirect = set()
        for edge in affected:
            other = edge["to"] if filename in edge["from"] else edge["from"]
            for e2 in self.edges:
                if other in e2["from"] or other in e2["to"]:
                    if e2["from"] != filename and e2["to"] != filename:
                        indirect.add(f"{e2['from']} --[{e2['relation']}]--> {e2['to']}")
        
        if indirect:
            print(f"\n  Indirect dependencies ({len(indirect)}):")
            for dep in list(indirect)[:10]:
                print(f"    ⚠️  {dep}")

def main():
    kg = KnowledgeGraph()
    
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == "build":
        kg.build()
    elif command == "search" and len(sys.argv) >= 3:
        kg.search(" ".join(sys.argv[2:]))
    elif command == "stats":
        if kg.load():
            stats = kg.get_stats()
            print(f"\n[GRAPH] Stats:")
            print(f"  Nodes: {stats['total_nodes']}")
            print(f"  Edges: {stats['total_edges']}")
            print(f"  By type: {json.dumps(stats['by_type'], indent=4)}")
        else:
            kg.build()
    elif command == "impact" and len(sys.argv) >= 3:
        kg.impact(sys.argv[2])
    else:
        print(f"[ERROR] Unknown command: {command}")

if __name__ == "__main__":
    main()
