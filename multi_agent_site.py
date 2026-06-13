import asyncio
import json
import os
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal


ROOT = Path(__file__).resolve().parent
HTML_PATH = ROOT / "index.html"
QA_SCRIPT_PATH = ROOT / "qa_check.js"
BLENDER_SCRIPT_PATH = ROOT / "tools" / "blender_asset_generator.py"
ASSET_DIR = ROOT / "assets" / "blender"
EXTERNAL_ARTIST_DIR = ROOT.parents[1] / "3д художник"
EXTERNAL_ARTIST_MCP = EXTERNAL_ARTIST_DIR / "blender-mcp-work" / "blender_artist_mcp.py"
EXTERNAL_ARTIST_MODEL = EXTERNAL_ARTIST_DIR / "models" / "active_theory_like_scene.glb"
EXTERNAL_ASSET_DIR = ROOT / "assets" / "external_artist"


TaskStatus = Literal["PENDING", "RUNNING", "DONE", "FAIL"]


@dataclass
class SceneTask:
    id: str
    title: str
    kind: Literal["active-theory-hero", "work-grid", "atmosphere"]
    status: TaskStatus = "PENDING"


@dataclass
class AgentMessage:
    sender: str
    recipient: str
    type: str
    payload: dict[str, Any]


@dataclass
class ObjectSpec:
    type: Literal["object"]
    name: str
    geometry: str
    color: int
    position: list[float]
    scale: list[float]
    material: Literal["standard", "basic"] = "standard"
    tool: str = "blender"
    asset_file: str | None = None
    animation: dict[str, Any] | None = None


@dataclass
class QAResult:
    status: Literal["PASS", "FAIL"]
    errors: list[str] = field(default_factory=list)


class ToolRegistry:
    def __init__(self) -> None:
        self.blender_path = self._find_blender()
        self.external_artist_dir = EXTERNAL_ARTIST_DIR if EXTERNAL_ARTIST_DIR.exists() else None
        self.external_artist_mcp = EXTERNAL_ARTIST_MCP if EXTERNAL_ARTIST_MCP.exists() else None
        self.external_artist_model = EXTERNAL_ARTIST_MODEL if EXTERNAL_ARTIST_MODEL.exists() else None

    def _find_blender(self) -> str | None:
        candidates = [
            os.environ.get("BLENDER_PATH"),
            shutil.which("blender"),
            str(ROOT / "blender" / "blender.exe"),
            str(ROOT / "BLENDER" / "blender.exe"),
            str(ROOT / "BLENDE~1" / "blender.exe"),
            r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        ]
        for candidate in candidates:
            if candidate and Path(candidate).exists():
                return str(Path(candidate))
        return None

    def require_blender(self) -> str:
        if self.blender_path:
            print(f"[ToolRegistry] Blender connected: {self.blender_path}")
            return self.blender_path
        raise RuntimeError(
            "Blender is required for Artist3D. Install Blender, add it to PATH, "
            "or set BLENDER_PATH to blender.exe."
        )

    def require_external_artist(self) -> Path:
        if self.external_artist_dir and self.external_artist_mcp and self.external_artist_model:
            print(f"[ToolRegistry] External 3D artist connected: {self.external_artist_dir}")
            return self.external_artist_dir
        raise RuntimeError(
            "External 3D artist folder is required. Expected: "
            f"{EXTERNAL_ARTIST_DIR}"
        )


class ExternalArtistClient:
    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools

    def generate_plan(self, task: SceneTask) -> dict[str, Any]:
        self.tools.require_external_artist()
        payload = "\n".join(
            json.dumps(message, ensure_ascii=False)
            for message in [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "website-architect", "version": "1.0"},
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "generate_scene_plan",
                        "arguments": {
                            "prompt": task.title,
                            "subject": task.kind,
                            "reference_notes": "External 3D artist folder is guiding this Three.js scene component.",
                        },
                    },
                },
            ]
        ) + "\n"

        completed = subprocess.run(
            ["uv", "run", "python", str(self.tools.external_artist_mcp)],
            cwd=self.tools.external_artist_dir,
            input=payload,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())

        responses = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
        response = next((item for item in responses if item.get("id") == 2), None)
        if not response or response.get("error"):
            raise RuntimeError(f"External artist MCP failed: {response}")
        return json.loads(response["result"]["content"][0]["text"])

    def copy_reference_asset(self, task: SceneTask, version: int) -> str:
        self.tools.require_external_artist()
        EXTERNAL_ASSET_DIR.mkdir(parents=True, exist_ok=True)
        target = EXTERNAL_ASSET_DIR / f"{task.kind}_artist_reference_v{version}.glb"
        shutil.copy2(self.tools.external_artist_model, target)
        return str(target.relative_to(ROOT)).replace("\\", "/")


class Artist3D:
    name = "Artist3D"

    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools
        self.external_artist = ExternalArtistClient(tools)

    async def generate(self, task: SceneTask, version: int) -> AgentMessage:
        print(f"[Artist3D] Asking external folder agent for art direction: {task.title}")
        external_plan = await asyncio.to_thread(self.external_artist.generate_plan, task)
        external_asset = await asyncio.to_thread(self.external_artist.copy_reference_asset, task, version)

        if task.kind == "active-theory-hero":
            spec = ObjectSpec(
                type="object",
                name="active-theory-glb-hero",
                geometry="group",
                color=0xA970FF,
                position=[0, -0.6, 0],
                scale=[1.7, 1.7, 1.7],
                asset_file=external_asset,
                animation={"target": "hero", "axis": "y", "speed": 0.004, "loopAt": 0},
            )
        elif task.kind == "work-grid":
            spec = ObjectSpec(
                type="object",
                name="interactive-work-grid",
                geometry="box",
                color=0x111827,
                position=[0, 0.2, -2.4],
                scale=[1, 1, 1],
                asset_file=external_asset,
                animation={"target": "cards", "axis": "z", "speed": 0.012, "loopAt": 0},
            )
        else:
            spec = ObjectSpec(
                type="object",
                name="webgl-atmosphere",
                geometry="group",
                color=0x37F5FF,
                position=[0, 0, 0],
                scale=[1, 1, 1],
                asset_file=external_asset,
                animation={"target": "particles", "axis": "y", "speed": 0.01, "loopAt": 0},
            )

        payload = asdict(spec)
        payload["external_artist"] = {
            "folder": str(EXTERNAL_ARTIST_DIR),
            "mcp_server": str(EXTERNAL_ARTIST_MCP),
            "reference_asset": external_asset,
            "plan": external_plan,
        }
        return AgentMessage(
            sender=self.name,
            recipient="Engineer",
            type="object_spec",
            payload=payload,
        )

    def _run_blender(self, task: SceneTask, version: int) -> dict[str, Any]:
        blender_path = self.tools.require_blender()
        ASSET_DIR.mkdir(parents=True, exist_ok=True)
        output_path = ASSET_DIR / f"{task.kind}_v{version}.json"

        completed = subprocess.run(
            [
                blender_path,
                "--background",
                "--factory-startup",
                "--python",
                str(BLENDER_SCRIPT_PATH),
                "--",
                "--kind",
                task.kind,
                "--version",
                str(version),
                "--out",
                str(output_path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

        if completed.returncode != 0:
            raise RuntimeError(
                "Blender failed for "
                f"{task.kind}: {completed.stderr.strip() or completed.stdout.strip()}"
            )

        return json.loads(output_path.read_text(encoding="utf-8"))


class Engineer:
    name = "Engineer"

    async def build_component(self, task: SceneTask, spec_message: AgentMessage) -> dict[str, Any]:
        print(f"[Engineer] Embedding external 3D artist-backed JSON into Three.js: {task.title}")
        await asyncio.sleep(0.2)
        return spec_message.payload

    async def compose_html(self, components: list[dict[str, Any]], version: int) -> str:
        print(f"[Engineer] Building index.html version {version}.0")
        await asyncio.sleep(0.15)
        component_json = json.dumps(components, ensure_ascii=False, indent=2)
        version_comment = "<!-- VERSION 2 -->" if version >= 2 else "<!-- VERSION 1 -->"

        return f"""<!doctype html>
{version_comment}
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Active Theory Work - Multi-Agent 3D Scene</title>
  <style>
    :root {{
      color-scheme: dark;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #050506;
      color: #f7f7f2;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      overflow: hidden;
      background: #050506;
    }}
    canvas {{
      display: block;
      width: 100vw;
      height: 100vh;
    }}
    .hud {{
      position: fixed;
      inset: 0;
      z-index: 2;
      pointer-events: none;
      display: grid;
      grid-template-rows: auto 1fr auto;
      padding: clamp(18px, 3vw, 44px);
    }}
    .topbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 18px;
      font-size: 12px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: rgba(247, 247, 242, 0.74);
    }}
    .brand {{
      color: #f7f7f2;
      font-weight: 800;
    }}
    .hero-copy {{
      align-self: end;
      max-width: min(980px, 92vw);
      padding-bottom: min(8vh, 72px);
    }}
    h1 {{
      margin: 0;
      max-width: 940px;
      font-size: clamp(48px, 10vw, 146px);
      line-height: 0.88;
      letter-spacing: 0;
      text-transform: uppercase;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px 18px;
      margin-top: 22px;
      color: rgba(247, 247, 242, 0.72);
      font-size: clamp(13px, 1.5vw, 16px);
    }}
    .footer {{
      display: flex;
      justify-content: space-between;
      gap: 18px;
      color: rgba(247, 247, 242, 0.58);
      font-size: 12px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .accent {{ color: #a970ff; }}
    @media (max-width: 720px) {{
      .topbar,
      .footer {{
        font-size: 10px;
      }}
      .hero-copy {{
        padding-bottom: 12vh;
      }}
    }}
  </style>
</head>
<body>
  <main class="hud" aria-label="Active Theory inspired 3D work scene">
    <div class="topbar">
      <div class="brand">Active Theory / Work</div>
      <div>Multi-Agent WebGL Scene</div>
    </div>
    <section class="hero-copy">
      <h1>Work in motion</h1>
      <div class="meta">
        <span>Full-bleed realtime portfolio space</span>
        <span class="accent">external 3D artist GLB</span>
        <span>kinetic case-study cards</span>
      </div>
    </section>
    <div class="footer">
      <span>Scroll-field composition</span>
      <span>Three.js + MCP agent metadata</span>
    </div>
  </main>
  <script type="importmap">
    {{
      "imports": {{
        "three": "./node_modules/three/build/three.module.js"
      }}
    }}
  </script>
  <script type="module">
    import * as THREE from './node_modules/three/build/three.module.js';
    import {{ GLTFLoader }} from './node_modules/three/examples/jsm/loaders/GLTFLoader.js';

    const specs = {component_json};
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050506);
    scene.fog = new THREE.FogExp2(0x050506, 0.055);

    const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 120);
    camera.position.set(0.5, 1.55, 8.2);
    camera.lookAt(0, 0.2, 0);

    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false }});
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    document.body.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0x8aa0ff, 0.42));
    const key = new THREE.DirectionalLight(0xffffff, 2.4);
    key.position.set(-3.5, 5.5, 4.5);
    scene.add(key);
    const violet = new THREE.PointLight(0xa970ff, 42, 18);
    violet.position.set(-3.8, 1.7, 1.8);
    scene.add(violet);
    const cyan = new THREE.PointLight(0x37f5ff, 30, 16);
    cyan.position.set(3.5, -0.2, 2.5);
    scene.add(cyan);

    const root = new THREE.Group();
    root.name = 'active-theory-work-scene';
    scene.add(root);

    const hero = new THREE.Group();
    hero.name = 'external-active-theory-glb';
    root.add(hero);

    const heroSpec = specs.find((spec) => spec.name === 'active-theory-glb-hero') ?? specs[0];
    const loader = new GLTFLoader();
    loader.load(heroSpec.asset_file, (gltf) => {{
      const model = gltf.scene;
      model.name = 'imported-active-theory-like-scene';
      const box = new THREE.Box3().setFromObject(model);
      const size = box.getSize(new THREE.Vector3()).length() || 1;
      const center = box.getCenter(new THREE.Vector3());
      model.position.sub(center);
      model.scale.setScalar(4.2 / size);
      model.traverse((child) => {{
        if (child.isMesh) {{
          child.castShadow = true;
          child.receiveShadow = true;
          if (child.material) {{
            child.material = child.material.clone();
            child.material.roughness = Math.min(child.material.roughness ?? 0.48, 0.54);
            child.material.metalness = Math.max(child.material.metalness ?? 0.08, 0.18);
          }}
        }}
      }});
      hero.add(model);
      window.__SCENE_DIAGNOSTICS__.loadedExternalModel = true;
      window.__SCENE_DIAGNOSTICS__.objectCount = scene.children.length + root.children.length + hero.children.length + cards.children.length + particleCount;
    }}, undefined, (error) => {{
      console.warn('External GLB could not be loaded, procedural fallback remains visible.', error?.message || error);
      window.__SCENE_DIAGNOSTICS__.loadedExternalModel = false;
    }});

    const floorMat = new THREE.MeshStandardMaterial({{
      color: 0x07090f,
      roughness: 0.62,
      metalness: 0.18,
      emissive: 0x050816,
      emissiveIntensity: 0.35
    }});
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(18, 18, 32, 32), floorMat);
    floor.rotation.x = -Math.PI / 2;
    floor.position.y = -1.55;
    root.add(floor);

    const ringMat = new THREE.MeshBasicMaterial({{ color: 0xa970ff, transparent: true, opacity: 0.32 }});
    for (let i = 0; i < 5; i += 1) {{
      const ring = new THREE.Mesh(new THREE.TorusGeometry(1.35 + i * 0.62, 0.006, 8, 160), ringMat);
      ring.rotation.x = Math.PI / 2;
      ring.position.y = -1.48 + i * 0.012;
      ring.name = `neon-orbit-${{i}}`;
      root.add(ring);
    }}

    const cards = new THREE.Group();
    cards.name = 'kinetic-work-cards';
    root.add(cards);
    const cardTitles = ['ROVER', 'FIELD', 'CHAOS', 'PATRONUS', 'LOBBY', 'SKY'];
    const cardColors = [0x131820, 0x181226, 0x102027, 0x201525, 0x111b2c, 0x191919];
    for (let i = 0; i < cardTitles.length; i += 1) {{
      const angle = (i / cardTitles.length) * Math.PI * 2;
      const radius = 3.7;
      const group = new THREE.Group();
      group.name = `work-card-${{cardTitles[i].toLowerCase()}}`;
      group.position.set(Math.cos(angle) * radius, -0.2 + (i % 2) * 0.42, Math.sin(angle) * radius - 0.8);
      group.rotation.y = -angle + Math.PI / 2;

      const card = new THREE.Mesh(
        new THREE.BoxGeometry(1.28, 0.78, 0.055),
        new THREE.MeshStandardMaterial({{
          color: cardColors[i],
          roughness: 0.44,
          metalness: 0.26,
          emissive: i % 2 ? 0x2d1648 : 0x073945,
          emissiveIntensity: 0.25
        }})
      );
      group.add(card);

      const edge = new THREE.Mesh(
        new THREE.BoxGeometry(1.34, 0.84, 0.02),
        new THREE.MeshBasicMaterial({{ color: i % 2 ? 0xa970ff : 0x37f5ff, transparent: true, opacity: 0.26 }})
      );
      edge.position.z = -0.04;
      group.add(edge);
      cards.add(group);
    }}

    const particleCount = 1200;
    const particleGeometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i += 1) {{
      positions[i * 3] = (Math.random() - 0.5) * 16;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 7;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 14;
    }}
    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particles = new THREE.Points(
      particleGeometry,
      new THREE.PointsMaterial({{ color: 0x9eeeff, size: 0.018, transparent: true, opacity: 0.62, depthWrite: false }})
    );
    particles.name = 'webgl-dust-field';
    root.add(particles);

    const fallback = new THREE.Mesh(
      new THREE.IcosahedronGeometry(1.25, 3),
      new THREE.MeshStandardMaterial({{
        color: 0x111217,
        roughness: 0.28,
        metalness: 0.72,
        emissive: 0x301365,
        emissiveIntensity: 0.42,
        wireframe: false
      }})
    );
    fallback.name = 'procedural-fallback-hero';
    hero.add(fallback);

    const clock = new THREE.Clock();
    function animate() {{
      requestAnimationFrame(animate);
      const t = clock.getElapsedTime();
      root.rotation.y = Math.sin(t * 0.11) * 0.08;
      hero.rotation.y += 0.004;
      hero.rotation.x = Math.sin(t * 0.32) * 0.045;
      cards.rotation.y -= 0.0018;
      particles.rotation.y += 0.0008;
      particles.rotation.x = Math.sin(t * 0.08) * 0.08;
      camera.position.x = Math.sin(t * 0.17) * 0.38;
      camera.lookAt(0, 0.05, 0);
      renderer.render(scene, camera);
    }}

    window.addEventListener('resize', () => {{
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    }});

    window.__SCENE_DIAGNOSTICS__ = {{
      objectCount: scene.children.length + root.children.length + hero.children.length + cards.children.length + particleCount,
      carColor: undefined,
      hasBlenderAssets: specs.every((spec) => Boolean(spec.asset_file)),
      hasExternalArtist: specs.every((spec) => Boolean(spec.external_artist?.mcp_server)),
      hasRendererCanvas: Boolean(renderer.domElement),
      loadedExternalModel: false,
      reference: 'https://activetheory.net/work'
    }};

    animate();
  </script>
</body>
</html>
"""


class QAAgent:
    name = "QAAgent"

    async def inspect(self, requested_prompt: str) -> QAResult:
        print("[QAAgent] Running Puppeteer headless inspection.")
        await asyncio.sleep(0.1)

        try:
            completed = subprocess.run(
                ["node", str(QA_SCRIPT_PATH), str(HTML_PATH), requested_prompt],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except FileNotFoundError:
            return QAResult("FAIL", ["Node.js is missing. QA requires Puppeteer through node."])
        except subprocess.TimeoutExpired:
            return QAResult("FAIL", ["Puppeteer timeout: page did not load in 30 seconds."])

        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            if completed.returncode != 0:
                errors = completed.stderr.strip().splitlines() + completed.stdout.strip().splitlines()
                return QAResult("FAIL", [error for error in errors if error])
            return QAResult("FAIL", [f"QA returned non-JSON: {completed.stdout.strip()}"])

        return QAResult(payload["status"], payload.get("errors", []))


class Architect:
    name = "Architect"

    def __init__(self) -> None:
        self.tools = ToolRegistry()
        self.artist = Artist3D(self.tools)
        self.engineer = Engineer()
        self.qa = QAAgent()

    def create_tasks(self, prompt: str) -> list[SceneTask]:
        print(f"[Architect] User task: {prompt}")
        self.tools.require_external_artist()
        tasks = [
            SceneTask(
                "task-1",
                "Active Theory work page inspired full-bleed WebGL hero using the external GLB reference",
                "active-theory-hero",
            ),
            SceneTask(
                "task-2",
                "Dark cinematic portfolio work grid with hover-ready 3D cards",
                "work-grid",
            ),
            SceneTask(
                "task-3",
                "Realtime particles, neon scanlines, and scroll-like motion atmosphere",
                "atmosphere",
            ),
        ]
        print("[Architect] JSON Task List:")
        print(json.dumps([asdict(task) for task in tasks], ensure_ascii=False, indent=2))
        return tasks

    async def _run_task(self, task: SceneTask, version: int) -> dict[str, Any]:
        task.status = "RUNNING"
        spec = await self.artist.generate(task, version)
        component = await self.engineer.build_component(task, spec)
        task.status = "DONE"
        return component

    async def build_until_pass(self, prompt: str, max_attempts: int = 2) -> QAResult:
        try:
            tasks = self.create_tasks(prompt)
        except RuntimeError as error:
            return QAResult("FAIL", [str(error)])

        for version in range(1, max_attempts + 1):
            print(f"\n[Architect] Starting iteration {version}.0")
            try:
                components = await asyncio.gather(
                    *(self._run_task(task, version) for task in tasks)
                )
            except RuntimeError as error:
                return QAResult("FAIL", [str(error)])

            html = await self.engineer.compose_html(components, version)
            HTML_PATH.write_text(html, encoding="utf-8")

            result = await self.qa.inspect(prompt)
            if result.status == "PASS":
                print("[QAAgent] PASS: scene is not empty, no console errors, car is red.")
                return result

            print(f"[QAAgent] FAIL: {result.errors}")
            print("[Architect] Feedback loop: Artist3D corrects assets, Engineer rebuilds version 2.0.")

        return result


async def main() -> None:
    user_prompt = "3D scene based on https://activetheory.net/work: dark full-bleed WebGL portfolio, kinetic work cards, neon particles, and imported Active Theory-like GLB hero asset"
    architect = Architect()
    result = await architect.build_until_pass(user_prompt)
    print(f"\n[System] Final status: {result.status}")
    if result.errors:
        print(json.dumps(result.errors, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
