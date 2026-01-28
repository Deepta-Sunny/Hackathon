export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
}

export interface AttackState {
  running: boolean;
  current_category: string | null;
  current_run: number | null;
  current_turn: number | null;
  total_categories: number;
  total_runs_per_category: number;
  results: Record<string, unknown>;
  [key: string]: unknown;
}

export interface StatusResponse {
  attack_state: AttackState;
  active_connections: number;
  timestamp: string;
}

export interface AttackSummary {
  filename: string;
  attack_category?: string;
  run_number?: number;
  vulnerabilities_found?: number;
  total_turns?: number;
  start_time?: string;
  end_time?: string;
}

export interface AttackResultsResponse {
  results: AttackSummary[];
}

export interface ChatbotProfile {
  username: string;
  websocket_url: string;
  domain: string;
  primary_objective: string;
  intended_audience: string;
  chatbot_role: string;
  capabilities: string[];
  boundaries: string;
  communication_style: string;
  context_awareness: string;
}

export interface LegacyAttackPayload {
  websocketUrl: string;
  architectureFile: File;
}

export type StartAttackPayload = ChatbotProfile | LegacyAttackPayload;

export type AsyncState<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
};

export type ApiSliceState = {
  health: AsyncState<HealthResponse>;
  status: AsyncState<StatusResponse>;
  startAttack: AsyncState<unknown>;
  stopAttack: AsyncState<unknown>;
  results: AsyncState<AttackResultsResponse>;
  runResult: AsyncState<unknown>;
  monitorSocket: WebSocket | null;
  monitorConnecting: boolean;
  monitorOpen: boolean;
  monitorError: string | null;
};
