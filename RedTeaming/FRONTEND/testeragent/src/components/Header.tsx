import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";

export default function Header() {
  return (
    <Box>
      <AppBar position="fixed" color='inherit'>
        <Toolbar variant="dense">
          <Typography variant='h6' color={'#20a100ff'} component='header' fontFamily='inherit' fontWeight={700}>
            Botman_
          </Typography>
        </Toolbar>
      </AppBar>
    </Box>
  );
}
