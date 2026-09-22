import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormControl,
  FormLabel,
  Select,
  MenuItem,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TextField,
  Slider,
  Card,
  CardContent,
  Chip,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Divider
} from '@mui/material';
import DirectionsBusIcon from '@mui/icons-material/DirectionsBus';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import PersonIcon from '@mui/icons-material/Person';
import PhoneIcon from '@mui/icons-material/Phone';
import api from '../api';

export default function LeftPanel({ onSelectRoute, onFoundStops, onUserLocationChange }) {
  const [activeTab, setActiveTab] = useState(0);

  // Time slot & Route search state
  const [timeSlot, setTimeSlot] = useState('morning');
  const [routesList, setRoutesList] = useState([]);
  const [selectedRouteNumber, setSelectedRouteNumber] = useState('');
  const [routeDetails, setRouteDetails] = useState(null);
  const [loadingRoutes, setLoadingRoutes] = useState(false);
  const [loadingDetails, setLoadingDetails] = useState(false);

  // Nearest stop finder state
  const [latitude, setLatitude] = useState('13.090476'); // Paper Table I sample
  const [longitude, setLongitude] = useState('80.215826');
  const [radiusKm, setRadiusKm] = useState(2.0);
  const [nearestStops, setNearestStops] = useState([]);
  const [loadingNearest, setLoadingNearest] = useState(false);
  const [nearestError, setNearestError] = useState('');

  // Load routes when time slot changes
  useEffect(() => {
    async function loadSlotRoutes() {
      setLoadingRoutes(true);
      try {
        const routes = await api.getRoutes(timeSlot);
        setRoutesList(routes);
        if (routes.length > 0) {
          setSelectedRouteNumber(routes[0].route_number);
        } else {
          setSelectedRouteNumber('');
          setRouteDetails(null);
        }
      } catch (err) {
        console.error('Failed to load routes:', err);
      } finally {
        setLoadingRoutes(false);
      }
    }
    loadSlotRoutes();
  }, [timeSlot]);

  // Handle Search click
  const handleSearchRoute = async () => {
    if (!selectedRouteNumber) return;
    setLoadingDetails(true);
    try {
      const details = await api.getRouteDetails(selectedRouteNumber);
      setRouteDetails(details);
      if (onSelectRoute) {
        onSelectRoute(details);
      }
    } catch (err) {
      console.error('Failed to fetch route details:', err);
    } finally {
      setLoadingDetails(false);
    }
  };

  // Handle Find Nearest Stop click
  const handleFindNearest = async () => {
    if (!latitude || !longitude) {
      setNearestError('Please enter valid latitude and longitude coordinates.');
      return;
    }
    setNearestError('');
    setLoadingNearest(true);
    try {
      const res = await api.findNearestStop(latitude, longitude, radiusKm);
      setNearestStops(res.stops || []);
      if (onFoundStops) {
        onFoundStops(res.stops || [], {
          latitude: parseFloat(latitude),
          longitude: parseFloat(longitude),
        });
      }
      if (onUserLocationChange) {
        onUserLocationChange({
          latitude: parseFloat(latitude),
          longitude: parseFloat(longitude),
        });
      }
    } catch (err) {
      setNearestError('Error querying nearest stops. Verify coordinates and backend connection.');
    } finally {
      setLoadingNearest(false);
    }
  };

  return (
    <Box sx={{ p: 2, height: '100%', overflowY: 'auto' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <DirectionsBusIcon sx={{ color: '#003366', mr: 1, fontSize: 30 }} />
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#003366' }}>
          VIT Chennai Bus Route Finder
        </Typography>
      </Box>
      <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mb: 2 }}>
        Standard System (ICCCNT 2024 Conference Baseline)
      </Typography>

      <Paper square elevation={0} sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={(e, val) => setActiveTab(val)}>
          <Tab label="Route Lookup" icon={<DirectionsBusIcon />} iconPosition="start" />
          <Tab label="Nearest Stop Finder" icon={<MyLocationIcon />} iconPosition="start" />
        </Tabs>
      </Paper>

      {/* TAB 0: ROUTE LOOKUP BY TIME SLOT */}
      {activeTab === 0 && (
        <Box>
          <FormControl component="fieldset" sx={{ mb: 2 }}>
            <FormLabel component="legend" sx={{ fontWeight: 600, fontSize: '0.85rem' }}>
              Select Time Slot
            </FormLabel>
            <RadioGroup
              row
              value={timeSlot}
              onChange={(e) => setTimeSlot(e.target.value)}
            >
              <FormControlLabel value="morning" control={<Radio size="small" />} label="Morning" />
              <FormControlLabel value="afternoon" control={<Radio size="small" />} label="Afternoon" />
              <FormControlLabel value="evening" control={<Radio size="small" />} label="Evening" />
            </RadioGroup>
          </FormControl>

          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <FormControl fullWidth size="small">
              <Select
                value={selectedRouteNumber}
                onChange={(e) => setSelectedRouteNumber(e.target.value)}
                disabled={loadingRoutes || routesList.length === 0}
                displayEmpty
              >
                {routesList.map((r) => (
                  <MenuItem key={r.route_number} value={r.route_number}>
                    Route {r.route_number} — {r.route_name} ({r.bus_type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button
              variant="contained"
              onClick={handleSearchRoute}
              disabled={loadingDetails || !selectedRouteNumber}
              sx={{ backgroundColor: '#003366', minWidth: 100 }}
            >
              {loadingDetails ? <CircularProgress size={20} color="inherit" /> : 'Search'}
            </Button>
          </Box>

          {/* Route Details Card */}
          {routeDetails && (
            <Box sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                  Route {routeDetails.route_number}: {routeDetails.route_name}
                </Typography>
                <Chip
                  label={routeDetails.bus_type}
                  size="small"
                  color={routeDetails.bus_type === 'AC' ? 'primary' : 'default'}
                />
              </Box>

              {/* Driver & In-Charge Contact Cards */}
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Card variant="outlined" sx={{ flex: 1, p: 1, bgcolor: '#f8fafc' }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center' }}>
                    <PersonIcon fontSize="inherit" sx={{ mr: 0.5 }} /> Driver Details
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {routeDetails.driver_name}
                  </Typography>
                  <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', color: 'primary.main' }}>
                    <PhoneIcon fontSize="inherit" sx={{ mr: 0.5 }} /> {routeDetails.driver_phone}
                  </Typography>
                </Card>

                <Card variant="outlined" sx={{ flex: 1, p: 1, bgcolor: '#f8fafc' }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center' }}>
                    <PersonIcon fontSize="inherit" sx={{ mr: 0.5 }} /> Faculty In-Charge
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    {routeDetails.incharge_name}
                  </Typography>
                  <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', color: 'primary.main' }}>
                    <PhoneIcon fontSize="inherit" sx={{ mr: 0.5 }} /> {routeDetails.incharge_phone}
                  </Typography>
                </Card>
              </Box>

              {/* Stops Table */}
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                Scheduled Stops & Timings ({routeDetails.stops.length} stops)
              </Typography>
              <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 240 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 700, width: 40 }}>#</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Stop Name</TableCell>
                      <TableCell sx={{ fontWeight: 700, width: 100 }}>Timing</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {routeDetails.stops.map((s, idx) => (
                      <TableRow key={idx} hover>
                        <TableCell>{idx + 1}</TableCell>
                        <TableCell>{s.name}</TableCell>
                        <TableCell sx={{ fontWeight: 600, color: '#003366' }}>{s.timing}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </Box>
      )}

      {/* TAB 1: NEAREST STOP FINDER (HAVERSINE) */}
      {activeTab === 1 && (
        <Box>
          <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
            Enter your GPS coordinates to calculate the nearest bus stops within radius using the Haversine formula.
          </Typography>

          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              label="Latitude"
              size="small"
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              fullWidth
            />
            <TextField
              label="Longitude"
              size="small"
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              fullWidth
            />
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" sx={{ fontWeight: 600 }}>
              Search Radius: {radiusKm} km
            </Typography>
            <Slider
              value={radiusKm}
              min={0.5}
              max={10.0}
              step={0.5}
              onChange={(e, val) => setRadiusKm(val)}
              valueLabelDisplay="auto"
              sx={{ color: '#003366' }}
            />
          </Box>

          <Button
            variant="contained"
            fullWidth
            onClick={handleFindNearest}
            disabled={loadingNearest}
            sx={{ backgroundColor: '#003366', mb: 2 }}
          >
            {loadingNearest ? <CircularProgress size={20} color="inherit" /> : 'Find Nearest Stops'}
          </Button>

          {nearestError && <Alert severity="error" sx={{ mb: 2 }}>{nearestError}</Alert>}

          {nearestStops.length > 0 && (
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                Found {nearestStops.length} stops within {radiusKm} km (Sorted by Haversine Distance):
              </Typography>
              <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 260 }}>
                <Table size="small" stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 700 }}>Stop Name</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Route</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Dist (km)</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Time</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {nearestStops.map((st, i) => (
                      <TableRow key={i} hover>
                        <TableCell sx={{ fontWeight: 600 }}>{st.stop_name}</TableCell>
                        <TableCell>
                          <Chip label={`R-${st.route_number}`} size="small" />
                        </TableCell>
                        <TableCell sx={{ color: 'primary.main', fontWeight: 700 }}>
                          {st.distance_km} km
                        </TableCell>
                        <TableCell>{st.timing}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
}
