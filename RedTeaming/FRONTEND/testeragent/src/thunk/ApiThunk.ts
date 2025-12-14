import { createAsyncThunk } from "@reduxjs/toolkit";
import {
  getHealth,
  getResults,
  getRunResult,
  getStatus,
  openAttackMonitorSocket,
  startAttack,
  stopAttack,
} from "../services/ApiService";
import type {
  AttackResultsResponse,
  HealthResponse,
  StartAttackPayload,
  StatusResponse,
} from "../types/Types";

const toErrorMessage = (error: unknown) => {
  if (error instanceof Error) {
    return error.message;
  }
  return typeof error === "string" ? error : "Unknown error";
};

export const fetchHealth = createAsyncThunk<
  HealthResponse,
  void,
  { rejectValue: string }
>("api/fetchHealth", async (_, { rejectWithValue }) => {
  try {
    return await getHealth();
  } catch (error) {
    return rejectWithValue(toErrorMessage(error));
  }
});

export const fetchStatus = createAsyncThunk<
  StatusResponse,
  void,
  { rejectValue: string }
>("api/fetchStatus", async (_, { rejectWithValue }) => {
  try {
    return await getStatus();
  } catch (error) {
    return rejectWithValue(toErrorMessage(error));
  }
});

export const initiateAttack = createAsyncThunk<
  unknown,
  StartAttackPayload,
  { rejectValue: string }
>("api/initiateAttack", async (payload, { rejectWithValue }) => {
  try {
    return await startAttack(payload);
  } catch (error) {
    return rejectWithValue(toErrorMessage(error));
  }
});

export const haltAttack = createAsyncThunk<
  unknown,
  void,
  { rejectValue: string }
>("api/haltAttack", async (_, { rejectWithValue }) => {
  try {
    return await stopAttack();
  } catch (error) {
    return rejectWithValue(toErrorMessage(error));
  }
});

export const fetchResults = createAsyncThunk<
  AttackResultsResponse,
  void,
  { rejectValue: string }
>("api/fetchResults", async (_, { rejectWithValue }) => {
  try {
    return await getResults();
  } catch (error) {
    return rejectWithValue(toErrorMessage(error));
  }
});

export const fetchRunResult = createAsyncThunk<
  unknown,
  { category: string; runNumber: number },
  { rejectValue: string }
>("api/fetchRunResult", async (args, { rejectWithValue }) => {
  try {
    return await getRunResult(args.category, args.runNumber);
  } catch (error) {
    return rejectWithValue(toErrorMessage(error));
  }
});

export const openAttackMonitor = createAsyncThunk<
  WebSocket,
  void,
  { rejectValue: string }
>("api/openAttackMonitor", async (_, { rejectWithValue }) => {
  try {
    return openAttackMonitorSocket();
  } catch (error) {
    return rejectWithValue(toErrorMessage(error));
  }
});
