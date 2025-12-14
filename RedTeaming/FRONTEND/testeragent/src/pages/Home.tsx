import { Box } from "@mui/material";
import Header from "../components/Header";
import InputForm from "../components/InputForm";
import ChatPanel from "../components/ChatPanel";
import ReportsPanel from "../components/ReportsPanel";

function Home() {
  return (
    <Box>
      <Header />
      <Box display={"flex"} flexDirection={"column"} gap={2} marginTop={4}>
        <InputForm onSubmit={() => {}} />
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
