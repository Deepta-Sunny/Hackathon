import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type {
  ApiSliceState,
  AsyncState,
  AttackResultsResponse,
  HealthResponse,
  StatusResponse,
} from "../types/Types";
import {
  fetchHealth,
  fetchResults,
  fetchRunResult,
  fetchStatus,
  haltAttack,
  initiateAttack,
  openAttackMonitor,
} from "../thunk/ApiThunk";

const createAsyncState = <T>(): AsyncState<T> => ({
  data: null,
  loading: false,
  error: null,
});

const initialState: ApiSliceState = {
  health: createAsyncState<HealthResponse>(),
  status: createAsyncState<StatusResponse>(),
  startAttack: createAsyncState<unknown>(),
  stopAttack: createAsyncState<unknown>(),
  results: createAsyncState<AttackResultsResponse>(),
  runResult: createAsyncState<unknown>(),
  monitorSocket: null,
  monitorConnecting: false,
  monitorOpen: false,
  monitorError: null,
};

const apiSlice = createSlice({
  name: "api",
  initialState,
  reducers: {
    clearMonitor(state) {
      state.monitorOpen = false;
      state.monitorSocket = null;
      state.monitorError = null;
      state.monitorConnecting = false;
    },
    setMonitorOpen(state, action: PayloadAction<boolean>) {
      state.monitorOpen = action.payload;
      state.monitorConnecting = false;
    },
    clearRunResult(state) {
      state.runResult.data = null;
      state.runResult.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHealth.pending, (state) => {
        state.health.loading = true;
        state.health.error = null;
      })
      .addCase(fetchHealth.fulfilled, (state, action) => {
        state.health.loading = false;
        state.health.data = action.payload;
      })
      .addCase(fetchHealth.rejected, (state, action) => {
        state.health.loading = false;
        state.health.error =
          action.payload ?? action.error.message ?? "Failed to fetch health";
      })
      .addCase(fetchStatus.pending, (state) => {
        state.status.loading = true;
        state.status.error = null;
      })
      .addCase(fetchStatus.fulfilled, (state, action) => {
        state.status.loading = false;
        state.status.data = action.payload;
      })
      .addCase(fetchStatus.rejected, (state, action) => {
        state.status.loading = false;
        state.status.error =
          action.payload ?? action.error.message ?? "Failed to fetch status";
      })
      .addCase(initiateAttack.pending, (state) => {
        state.startAttack.loading = true;
        state.startAttack.error = null;
      })
      .addCase(initiateAttack.fulfilled, (state, action) => {
        state.startAttack.loading = false;
        state.startAttack.data = action.payload;
      })
      .addCase(initiateAttack.rejected, (state, action) => {
        state.startAttack.loading = false;
        state.startAttack.error =
          action.payload ?? action.error.message ?? "Failed to start attack";
      })
      .addCase(haltAttack.pending, (state) => {
        state.stopAttack.loading = true;
        state.stopAttack.error = null;
      })
      .addCase(haltAttack.fulfilled, (state, action) => {
        state.stopAttack.loading = false;
        state.stopAttack.data = action.payload;
      })
      .addCase(haltAttack.rejected, (state, action) => {
        state.stopAttack.loading = false;
        state.stopAttack.error =
          action.payload ?? action.error.message ?? "Failed to stop attack";
      })
      .addCase(fetchResults.pending, (state) => {
        state.results.loading = true;
        state.results.error = null;
      })
      .addCase(fetchResults.fulfilled, (state, action) => {
        state.results.loading = false;
        state.results.data = action.payload;
      })
      .addCase(fetchResults.rejected, (state, action) => {
        state.results.loading = false;
        state.results.error =
          action.payload ?? action.error.message ?? "Failed to fetch results";
      })
      .addCase(fetchRunResult.pending, (state) => {
        state.runResult.loading = true;
        state.runResult.error = null;
      })
      .addCase(fetchRunResult.fulfilled, (state, action) => {
        state.runResult.loading = false;
        state.runResult.data = action.payload;
      })
      .addCase(fetchRunResult.rejected, (state, action) => {
        state.runResult.loading = false;
        state.runResult.error =
          action.payload ??
          action.error.message ??
          "Failed to fetch run result";
      })
      .addCase(openAttackMonitor.pending, (state) => {
        state.monitorConnecting = true;
        state.monitorOpen = false;
        state.monitorError = null;
      })
      .addCase(openAttackMonitor.fulfilled, (state, action) => {
        state.monitorConnecting = action.payload.readyState !== WebSocket.OPEN;
        state.monitorSocket = action.payload;
        state.monitorOpen = action.payload.readyState === WebSocket.OPEN;
      })
      .addCase(openAttackMonitor.rejected, (state, action) => {
        state.monitorConnecting = false;
        state.monitorOpen = false;
        state.monitorError =
          action.payload ??
          action.error.message ??
          "Failed to open attack monitor";
      });
  },
});

export const { clearMonitor, clearRunResult, setMonitorOpen } =
  apiSlice.actions;

export default apiSlice.reducer;
