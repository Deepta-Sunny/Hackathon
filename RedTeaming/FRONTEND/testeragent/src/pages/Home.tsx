import { Box } from "@mui/material";
import { useCallback } from "react";
import { useDispatch } from "react-redux";
import Header from "../components/Header";
import InputForm from "../components/InputForm";
import ChatPanel from "../components/ChatPanel";
import ReportsPanel from "../components/ReportsPanel";
import type { AppDispatch } from "../store/Store";
import { initiateAttack } from "../thunk/ApiThunk";

function Home() {
  const dispatch = useDispatch<AppDispatch>();

  const handleSubmit = useCallback(
    ({ file, query }: { file: File | null; query: string }) => {
      if (!file) {
        return;
      }

      dispatch(
        initiateAttack({
          websocketUrl: query,
          architectureFile: file,
        })
      );
    },
    [dispatch]
  );

  return (
    <Box>
      <Header />
      <Box display={"flex"} flexDirection={"column"} gap={2} marginTop={4}>
        <InputForm onSubmit={handleSubmit} />
        <Box display={"flex"} gap={2} height={"75vh"}>
          <Box flex={1} display={"flex"}>
            <ChatPanel />
          </Box>
          <Box flex={1} display={"flex"}>
            <ReportsPanel />
          </Box>
        </Box>
      </Box>
    </Box>
  );
}

export default Home;
