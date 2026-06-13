export type AgentName = 'Architect' | 'Artist3D' | 'Engineer' | 'QAAgent';
export type TaskStatus = 'PENDING' | 'RUNNING' | 'DONE' | 'FAIL';
export type SceneTaskKind = 'ground' | 'car' | 'motion';

export interface SceneTask {
  id: string;
  title: string;
  kind: SceneTaskKind;
  status: TaskStatus;
}

export interface AgentMessage<TPayload extends Record<string, unknown>> {
  sender: AgentName;
  recipient: AgentName;
  type: 'task_list' | 'object_spec' | 'html_code' | 'qa_result' | 'feedback';
  payload: TPayload;
}

export interface ObjectSpec {
  type: 'object';
  name: string;
  geometry: 'box' | 'sphere' | 'group';
  color: number;
  position: [number, number, number];
  scale: [number, number, number];
  material: 'standard' | 'basic';
  tool: 'blender';
  asset_file: string;
  external_artist?: {
    folder: string;
    mcp_server: string;
    reference_asset: string;
    plan: Record<string, unknown>;
  };
  blender?: {
    tool: 'Blender';
    blender_version: string;
    kind: SceneTaskKind;
    version: number;
    asset_file: string;
    object_count: number;
    dominant_color: number;
  };
  animation?: {
    target: 'car';
    axis: 'x' | 'y' | 'z';
    speed: number;
    loopAt: number;
  };
}

export interface QAResult {
  status: 'PASS' | 'FAIL';
  errors: string[];
}
