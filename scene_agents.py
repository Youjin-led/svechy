import argparse
import json
import os
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
UV_CACHE_DIR = ROOT / ".uv-cache"
EXTERNAL_ARTIST_DIR = ROOT.parents[1] / "3д художник"
EXTERNAL_MCP_DIR = EXTERNAL_ARTIST_DIR / "blender-mcp-work"
EXTERNAL_MCP = EXTERNAL_MCP_DIR / "blender_artist_mcp.py"
REFERENCE_REFINER = ROOT / "tools" / "refine_active_theory_references.py"


Workflow = Literal["active_theory_work", "general_prompt"]
Status = Literal["PASS", "FAIL"]


@dataclass
class SceneRequest:
    prompt: str
    workflow: Workflow
    subject: str
    style: str
    output_name: str = "agent_scene"


@dataclass
class ArtifactSet:
    blend: Path | None = None
    glb: Path | None = None
    preview: Path | None = None
    source_script: Path | None = None


@dataclass
class SceneReport:
    status: Status
    request: SceneRequest
    artifacts: dict[str, str | None]
    art_plan: dict[str, Any] | None = None
    build_result: dict[str, Any] | None = None
    inspection: dict[str, Any] | None = None
    critique: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)


class ToolRegistry:
    def __init__(self) -> None:
        self.external_artist_dir = EXTERNAL_ARTIST_DIR if EXTERNAL_ARTIST_DIR.exists() else None
        self.external_mcp_dir = EXTERNAL_MCP_DIR if EXTERNAL_MCP_DIR.exists() else None
        self.external_mcp = EXTERNAL_MCP if EXTERNAL_MCP.exists() else None

    def require_external_artist(self) -> None:
        missing = []
        if not self.external_artist_dir:
            missing.append(str(EXTERNAL_ARTIST_DIR))
        if not self.external_mcp_dir:
            missing.append(str(EXTERNAL_MCP_DIR))
        if not self.external_mcp:
            missing.append(str(EXTERNAL_MCP))
        if missing:
            raise RuntimeError("Missing external 3D artist files: " + ", ".join(missing))
        print(f"[ToolRegistry] External 3D artist ready: {self.external_artist_dir}")


class MCPClient:
    def __init__(self, tools: ToolRegistry) -> None:
        self.tools = tools

    def call_many(self, calls: list[tuple[str, dict[str, Any]]], timeout: int = 600) -> list[dict[str, Any]]:
        self.tools.require_external_artist()
        messages: list[dict[str, Any]] = [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "scene-orchestrator", "version": "2.0"},
                },
            }
        ]
        for index, (name, arguments) in enumerate(calls, start=2):
            messages.append(
                {
                    "jsonrpc": "2.0",
                    "id": index,
                    "method": "tools/call",
                    "params": {"name": name, "arguments": arguments},
                }
            )

        env = os.environ.copy()
        env["UV_CACHE_DIR"] = str(UV_CACHE_DIR)
        env["PYTHONIOENCODING"] = "utf-8"
        completed = subprocess.run(
            ["uv", "run", "python", str(self.tools.external_mcp)],
            cwd=self.tools.external_mcp_dir,
            input="\n".join(json.dumps(message, ensure_ascii=False) for message in messages) + "\n",
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())

        by_id = {}
        for line in completed.stdout.splitlines():
            if line.strip():
                payload = json.loads(line)
                if "id" in payload:
                    by_id[payload["id"]] = payload

        results = []
        for index in range(2, len(calls) + 2):
            response = by_id.get(index)
            if not response or response.get("error"):
                raise RuntimeError(f"MCP call failed: {response}")
            text = response["result"]["content"][0]["text"]
            results.append(json.loads(text))
        return results

    def call(self, name: str, arguments: dict[str, Any], timeout: int = 600) -> dict[str, Any]:
        return self.call_many([(name, arguments)], timeout=timeout)[0]


class ArchitectAgent:
    name = "ArchitectAgent"

    def plan(self, prompt: str) -> SceneRequest:
        normalized = prompt.lower()
        if "activetheory.net/work" in normalized or "active_theory_work" in normalized:
            request = SceneRequest(
                prompt=prompt,
                workflow="active_theory_work",
                subject="Active Theory inspired work-page 3D scene",
                style="dark cinematic WebGL portfolio, violet/cyan lighting, kinetic work-page composition",
                output_name="scene",
            )
        else:
            request = SceneRequest(
                prompt=prompt,
                workflow="general_prompt",
                subject=self._subject_from_prompt(prompt),
                style="cinematic production-ready Blender scene with strong silhouette, detailed materials, camera, lights, and preview render",
                output_name="scene",
            )
        print(f"[{self.name}] Workflow: {request.workflow}")
        print(f"[{self.name}] Subject: {request.subject}")
        return request

    def _subject_from_prompt(self, prompt: str) -> str:
        words = prompt.strip().split()
        return " ".join(words[:10]) or "custom 3D scene"


class ArtDirectorAgent:
    name = "ArtDirectorAgent"

    def __init__(self, mcp: MCPClient) -> None:
        self.mcp = mcp

    def create_brief(self, request: SceneRequest) -> dict[str, Any]:
        print(f"[{self.name}] Asking 3D artist MCP for a structured art brief.")
        return self.mcp.call(
            "generate_scene_plan",
            {
                "prompt": request.prompt,
                "subject": request.subject,
                "target_style": request.style,
                "reference_notes": "Return gates useful for a real Blender scene, not a web page mockup.",
            },
            timeout=120,
        )


class BlenderBuildAgent:
    name = "BlenderBuildAgent"

    def __init__(self, mcp: MCPClient) -> None:
        self.mcp = mcp

    def build(self, request: SceneRequest, attempt: int) -> tuple[dict[str, Any], ArtifactSet]:
        print(f"[{self.name}] Building real Blender artifacts through the external 3D artist.")
        if request.workflow == "active_theory_work":
            return self._build_active_theory()
        return self._build_general(request, attempt)

    def _build_active_theory(self) -> tuple[dict[str, Any], ArtifactSet]:
        script_path = EXTERNAL_MCP_DIR / "create_active_theory_work_page.py"
        code = (
            "import runpy\n"
            "from pathlib import Path\n"
            f"runpy.run_path({json.dumps(str(script_path))}, run_name='__main__')\n"
        )
        result = self.mcp.call(
            "run_blender_script",
            {"name": "active_theory_work_scene_orchestrated", "code": code, "timeout": 600},
            timeout=720,
        )
        artifacts = ArtifactSet(
            blend=EXTERNAL_MCP_DIR / "output" / "active_theory_work_page_scene.blend",
            glb=EXTERNAL_MCP_DIR / "output" / "active_theory_work_page_scene.glb",
            preview=EXTERNAL_MCP_DIR / "output" / "active_theory_work_page_preview.png",
            source_script=script_path,
        )
        return result, artifacts

    def _build_general(self, request: SceneRequest, attempt: int) -> tuple[dict[str, Any], ArtifactSet]:
        style = request.style
        if attempt > 1:
            style += "; revision pass: improve readability, add foreground/background depth, stronger lighting, more mesh detail"
        result = self.mcp.call(
            "generate_scene",
            {
                "prompt": request.prompt,
                "style": style,
                "output_name": f"{request.output_name}_v{attempt}",
                "render_preview": True,
                "export_glb": True,
                "timeout": 420,
            },
            timeout=540,
        )
        files = result.get("files", {})
        artifacts = ArtifactSet(
            blend=Path(files["blend"]) if files.get("blend") else None,
            glb=Path(files["glb"]) if files.get("glb") else None,
            preview=Path(files["preview"]) if files.get("preview") else None,
            source_script=Path(files["script"]) if files.get("script") else None,
        )
        return result, artifacts


class ReferenceRefinementAgent:
    name = "ReferenceRefinementAgent"

    def __init__(self, mcp: MCPClient) -> None:
        self.mcp = mcp

    def refine(self, request: SceneRequest, artifacts: ArtifactSet) -> tuple[dict[str, Any] | None, ArtifactSet]:
        if request.workflow != "active_theory_work":
            return None, artifacts
        print(f"[{self.name}] Running close-up reference similarity pass.")
        code = (
            "import runpy\n"
            f"runpy.run_path({json.dumps(str(REFERENCE_REFINER))}, run_name='__main__')\n"
        )
        result = self.mcp.call(
            "run_blender_script",
            {"name": "active_theory_reference_refinement", "code": code, "timeout": 720},
            timeout=840,
        )
        if result.get("exit_code") != 0:
            raise RuntimeError(result.get("stderr_tail") or result.get("stdout_tail") or "Reference refinement failed.")
        refined = ArtifactSet(
            blend=EXTERNAL_MCP_DIR / "output" / "active_theory_work_page_scene_refined.blend",
            glb=EXTERNAL_MCP_DIR / "output" / "active_theory_work_page_scene_refined.glb",
            preview=EXTERNAL_MCP_DIR / "output" / "active_theory_work_page_refined_preview.png",
            source_script=REFERENCE_REFINER,
        )
        return result, refined


class SimilarityReviewAgent:
    name = "SimilarityReviewAgent"

    def review(self, request: SceneRequest, artifacts: ArtifactSet, inspection: dict[str, Any] | None) -> list[str]:
        if request.workflow != "active_theory_work":
            return []
        errors: list[str] = []
        scene = (inspection or {}).get("scene") or {}
        if scene.get("objects", 0) < 3000:
            errors.append("Reference pass needs denser geometry/particles for the supplied Active Theory frames.")
        if artifacts.preview and artifacts.preview.exists() and artifacts.preview.stat().st_size < 1_500_000:
            errors.append("Preview is lighter than expected for the noisy/glassy reference style.")
        return errors

class SceneQAAgent:
    name = "SceneQAAgent"

    def __init__(self, mcp: MCPClient) -> None:
        self.mcp = mcp

    def inspect(self, artifacts: ArtifactSet) -> tuple[list[str], dict[str, Any] | None, dict[str, Any] | None]:
        print(f"[{self.name}] Inspecting .blend and preview through the 3D artist MCP.")
        errors: list[str] = []
        for label, path in [("blend", artifacts.blend), ("glb", artifacts.glb), ("preview", artifacts.preview)]:
            if not path or not path.exists():
                errors.append(f"Missing {label}: {path}")
            elif path.stat().st_size <= 1024:
                errors.append(f"{label} is too small: {path}")

        inspection = None
        critique = None
        if artifacts.blend and artifacts.blend.exists():
            inspection = self.mcp.call(
                "inspect_scene",
                {"blend_path": str(artifacts.blend), "timeout": 180},
                timeout=240,
            )
            scene = inspection.get("scene") or {}
            if scene.get("objects", 0) < 10:
                errors.append(f"Scene has too few objects: {scene.get('objects', 0)}")
            if scene.get("meshes", 0) < 3:
                errors.append(f"Scene has too few meshes: {scene.get('meshes', 0)}")
            if scene.get("lights", 0) < 1:
                errors.append("Scene has no lights.")
            if scene.get("cameras", 0) < 1:
                errors.append("Scene has no camera.")

        if artifacts.preview and artifacts.preview.exists():
            critique = self.mcp.call(
                "critique_preview",
                {"preview_path": str(artifacts.preview)},
                timeout=120,
            )
            if not critique.get("dimensions"):
                errors.append("Preview dimensions could not be read.")
            if critique.get("file_size_bytes", 0) < 10_000:
                errors.append("Preview file looks too small to be useful.")

        return errors, inspection, critique


class ArtifactAgent:
    name = "ArtifactAgent"

    def publish(self, artifacts: ArtifactSet) -> ArtifactSet:
        print(f"[{self.name}] Publishing final artifacts to local output/.")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        published = ArtifactSet()
        for attr, filename in [("blend", "scene.blend"), ("glb", "scene.glb"), ("preview", "preview.png")]:
            source = getattr(artifacts, attr)
            if source and source.exists():
                target = OUTPUT_DIR / filename
                shutil.copy2(source, target)
                setattr(published, attr, target)
        if artifacts.source_script and artifacts.source_script.exists():
            target = OUTPUT_DIR / "source_script.py"
            shutil.copy2(artifacts.source_script, target)
            published.source_script = target
        return published


class SceneOrchestrator:
    def __init__(self) -> None:
        tools = ToolRegistry()
        mcp = MCPClient(tools)
        self.architect = ArchitectAgent()
        self.art_director = ArtDirectorAgent(mcp)
        self.builder = BlenderBuildAgent(mcp)
        self.refiner = ReferenceRefinementAgent(mcp)
        self.similarity = SimilarityReviewAgent()
        self.qa = SceneQAAgent(mcp)
        self.artifacts = ArtifactAgent()

    def run(self, prompt: str, max_attempts: int = 2) -> SceneReport:
        request = self.architect.plan(prompt)
        art_plan = self.art_director.create_brief(request)
        last_report: SceneReport | None = None

        for attempt in range(1, max_attempts + 1):
            print(f"[SceneOrchestrator] Attempt {attempt}/{max_attempts}")
            try:
                build_result, raw_artifacts = self.builder.build(request, attempt)
                refinement_result, raw_artifacts = self.refiner.refine(request, raw_artifacts)
                if refinement_result:
                    build_result["reference_refinement"] = refinement_result
                errors, inspection, critique = self.qa.inspect(raw_artifacts)
                errors.extend(self.similarity.review(request, raw_artifacts, inspection))
                status: Status = "PASS" if not errors else "FAIL"
                published = self.artifacts.publish(raw_artifacts) if status == "PASS" else ArtifactSet()
                report = SceneReport(
                    status=status,
                    request=request,
                    artifacts=self._artifact_paths(published if status == "PASS" else raw_artifacts),
                    art_plan=art_plan,
                    build_result=build_result,
                    inspection=inspection,
                    critique=critique,
                    errors=errors,
                )
                last_report = report
                if status == "PASS":
                    self._write_report(report)
                    return report
                print(f"[SceneOrchestrator] QA failed: {errors}")
            except Exception as error:
                last_report = SceneReport(
                    status="FAIL",
                    request=request,
                    artifacts={},
                    art_plan=art_plan,
                    errors=[str(error)],
                )
                print(f"[SceneOrchestrator] Attempt failed: {error}")

            if request.workflow == "active_theory_work":
                break

        assert last_report is not None
        self._write_report(last_report)
        return last_report

    def _artifact_paths(self, artifacts: ArtifactSet) -> dict[str, str | None]:
        return {
            "blend": str(artifacts.blend) if artifacts.blend else None,
            "glb": str(artifacts.glb) if artifacts.glb else None,
            "preview": str(artifacts.preview) if artifacts.preview else None,
            "source_script": str(artifacts.source_script) if artifacts.source_script else None,
            "report": str(OUTPUT_DIR / "report.json"),
        }

    def _write_report(self, report: SceneReport) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "report.json").write_text(
            json.dumps(asdict(report), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a real 3D scene through local AI agents and the external 3D artist MCP.")
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Scene prompt. Example: npm start -- \"3D scene like activetheory.net/work\"",
    )
    parser.add_argument("--max-attempts", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    prompt = " ".join(args.prompt).strip() or "3D scene like activetheory.net/work"
    report = SceneOrchestrator().run(prompt, max_attempts=args.max_attempts)
    print(f"\n[System] Final status: {report.status}")
    print(json.dumps(report.artifacts, ensure_ascii=False, indent=2))
    if report.errors:
        print(json.dumps(report.errors, ensure_ascii=False, indent=2))
        raise SystemExit(2)


if __name__ == "__main__":
    main()
