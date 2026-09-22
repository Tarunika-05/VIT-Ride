import React, { useState } from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Chip,
  Paper,
  Grid,
  ThemeProvider,
  createTheme,
  CssBaseline
} from '@mui/material';
import DirectionsBusFilledIcon from '@mui/icons-material/DirectionsBusFilled';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import LeftPanel from './components/LeftPanel';
import ChatPanel from './components/ChatPanel';
import MapView from './components/MapView';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#003366', // Institutional Navy Blue
    },
    secondary: {
      main: '#0284c7', // AI Cyan / Light Blue
    },
    background: {
      default: '#f8fafc',
    },
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
});

export default function App() {
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [nearbyStops, setNearbyStops] = useState([]);

  const handleSelectRoute = (route) => {
    setSelectedRoute(route);
  };

  const handleFoundStops = (stops, coords) => {
    setNearbyStops(stops);
    setUserLocation(coords);
  };

  const handleUserLocationChange = (coords) => {
    setUserLocation(coords);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
        {/* Navigation Bar */}
        <AppBar position="static" elevation={1} sx={{ backgroundColor: '#003366' }}>
          <Toolbar variant="dense" sx={{ justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <DirectionsBusFilledIcon sx={{ color: '#ffffff' }} />
              <Typography variant="h6" sx={{ fontWeight: 700, fontSize: '1.1rem', letterSpacing: 0.3 }}>
                VIT-Ride — Campus Transit AI
              </Typography>
              <Chip
                label="Journal Extension"
                size="small"
                sx={{
                  backgroundColor: 'rgba(255, 255, 255, 0.15)',
                  color: '#ffffff',
                  fontSize: '0.7rem',
                  height: 22
                }}
              />
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                icon={<SmartToyIcon style={{ color: '#38bdf8', fontSize: 16 }} />}
                label="LangGraph Agent Active"
                size="small"
                sx={{ bgcolor: '#0f2942', color: '#e0f2fe', fontSize: '0.7rem' }}
              />
            </Box>
          </Toolbar>
        </AppBar>

        {/* Main Content Area */}
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', p: 1.5, gap: 1.5, overflowY: 'auto' }}>
          {/* Top Row: Dual Panels (Left: Conference App, Right: AI Chat) */}
          <Box sx={{ display: 'flex', gap: 1.5, flex: '1 1 55%', minHeight: '380px', flexWrap: { xs: 'wrap', md: 'nowrap' } }}>
            {/* LEFT PANEL: Conference Paper Interface */}
            <Paper
              elevation={2}
              sx={{
                flex: { xs: '1 1 100%', md: '1 1 50%' },
                height: { xs: '450px', md: '100%' },
                borderRadius: 2,
                overflow: 'hidden',
                bgcolor: '#ffffff'
              }}
            >
              <LeftPanel
                onSelectRoute={handleSelectRoute}
                onFoundStops={handleFoundStops}
                onUserLocationChange={handleUserLocationChange}
              />
            </Paper>

            {/* RIGHT PANEL: AI Chat Assistant */}
            <Paper
              elevation={2}
              sx={{
                flex: { xs: '1 1 100%', md: '1 1 50%' },
                height: { xs: '450px', md: '100%' },
                borderRadius: 2,
                overflow: 'hidden',
                bgcolor: '#ffffff'
              }}
            >
              <ChatPanel />
            </Paper>
          </Box>

          {/* Bottom Row: Shared Leaflet Map */}
          <Paper
            elevation={2}
            sx={{
              flex: '1 1 45%',
              minHeight: '320px',
              borderRadius: 2,
              overflow: 'hidden',
              position: 'relative'
            }}
          >
            <MapView
              selectedRoute={selectedRoute}
              userLocation={userLocation}
              nearbyStops={nearbyStops}
            />
          </Paper>
        </Box>
      </Box>
    </ThemeProvider>
  );
}
