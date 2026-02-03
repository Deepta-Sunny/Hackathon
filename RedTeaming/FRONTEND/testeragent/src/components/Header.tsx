import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { useNavigate, useLocation } from "react-router-dom";

export default function Header() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Box sx={{ flexGrow: 1, mb: 8 }}>
      <AppBar position="fixed" color='inherit' sx={{ backgroundColor: '#ffffff', borderBottom: '1px solid #e0e0e0', boxShadow: 'none' }}>
        <Toolbar variant="dense">
          <IconButton
            edge="start"
            aria-label="back"
            onClick={() => navigate('/')}
            sx={{ mr: 2, color: '#161616', display: location.pathname === '/' ? 'none' : 'flex' }}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant='h6' color={'#0f62fe'} component='header' fontFamily='inherit' fontWeight={700}>
            Response Analysis Dashbaord
          </Typography>
        </Toolbar>
      </AppBar>
    </Box>
  );
}
