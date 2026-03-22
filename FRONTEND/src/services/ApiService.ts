import axios from "axios";
import type {
  AttackResultsResponse,
  HealthResponse,
  StartAttackPayload,
  StatusResponse,
} from "../types/Types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

function buildWebSocketUrl(path: string): string {
  const url = new URL(API_BASE_URL);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname = path;
  url.search = "";
  url.hash = "";
  return url.toString();
}
export async function getHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>("/");
  return response.data;
}

export async function getStatus(): Promise<StatusResponse> {
  const response = await apiClient.get<StatusResponse>("/api/status");
  return response.data;
}

export async function startAttack(payload: StartAttackPayload) {
  // Check if it's a profile-based attack or legacy file upload
  if ('username' in payload) {
    // New profile-based attack
    const response = await apiClient.post("/api/attack/start-with-profile", payload, {
      headers: {
        "Content-Type": "application/json",
      },
    });
    return response.data;
  } else {
    // Legacy file upload (backward compatibility)
    const formData = new FormData();
    formData.append("websocket_url", payload.websocketUrl);
    formData.append("architecture_file", payload.architectureFile);

    const response = await apiClient.post("/api/attack/start", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  }
}

export async function stopAttack() {
  const response = await apiClient.post("/api/attack/stop");
  return response.data;
}

export async function getResults(): Promise<AttackResultsResponse> {
  const response = await apiClient.get<AttackResultsResponse>("/api/results");
  return response.data;
}

export async function getRunResult(category: string, runNumber: number) {
  const response = await apiClient.get(`/api/results/${category}/${runNumber}`);
  return response.data;
}

export function openAttackMonitorSocket() {
  const socketUrl = buildWebSocketUrl("/ws/attack-monitor");
  return new WebSocket(socketUrl);
}
