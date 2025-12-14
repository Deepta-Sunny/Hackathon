import { configureStore } from "@reduxjs/toolkit";
import apiReducer from "./Slice";

export const store = configureStore({
  reducer: {
    api: apiReducer,
  },
  devTools: true,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
