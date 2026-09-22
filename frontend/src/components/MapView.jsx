import React, { useEffect, useRef } from 'react';
import { Box, Typography } from '@mui/material';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap, Circle } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default icon URLs in bundled apps
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom Icon for VIT Chennai Campus
const campusIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Custom Icon for User's Search Location
const userIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Custom Icon for Nearby Stops
const nearbyIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [22, 36],
  iconAnchor: [11, 36],
  popupAnchor: [1, -30],
  shadowSize: [36, 36]
});

const VIT_CAMPUS_COORDS = [12.840658, 80.153187];

function MapController({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || 12);
    }
  }, [center, zoom, map]);
  return null;
}

export default function MapView({ selectedRoute, userLocation, nearbyStops }) {
  // Extract route path coordinates
  const routePolyline = selectedRoute?.stops?.map((s) => [s.latitude, s.longitude]) || [];

  // Determine center of map
  let mapCenter = VIT_CAMPUS_COORDS;
  let zoomLevel = 11;

  if (userLocation) {
    mapCenter = [userLocation.latitude, userLocation.longitude];
    zoomLevel = 13;
  } else if (routePolyline.length > 0) {
    mapCenter = routePolyline[0];
    zoomLevel = 12;
  }

  return (
    <Box sx={{ width: '100%', height: '100%', position: 'relative' }}>
      <MapContainer
        center={mapCenter}
        zoom={zoomLevel}
        style={{ width: '100%', height: '100%', borderRadius: '4px' }}
      >
        <MapController center={mapCenter} zoom={zoomLevel} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* 1. Permanent VIT Chennai Campus Marker */}
        <Marker position={VIT_CAMPUS_COORDS} icon={campusIcon}>
          <Popup>
            <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#dc2626' }}>
              🏛️ VIT Chennai Campus
            </Typography>
            <Typography variant="caption">Vandalur - Kelambakkam Road</Typography>
          </Popup>
        </Marker>

        {/* 2. User Search Location Marker */}
        {userLocation && (
          <>
            <Marker position={[userLocation.latitude, userLocation.longitude]} icon={userIcon}>
              <Popup>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#16a34a' }}>
                  📍 Your Search Location
                </Typography>
                <Typography variant="caption">
                  {userLocation.latitude.toFixed(6)}, {userLocation.longitude.toFixed(6)}
                </Typography>
              </Popup>
            </Marker>
            <Circle
              center={[userLocation.latitude, userLocation.longitude]}
              radius={2000} // 2km radius circle
              pathOptions={{ color: '#16a34a', fillColor: '#16a34a', fillOpacity: 0.1 }}
            />
          </>
        )}

        {/* 3. Selected Route Stops and Polyline */}
        {selectedRoute?.stops?.map((stop, idx) => (
          <Marker key={`route-stop-${idx}`} position={[stop.latitude, stop.longitude]}>
            <Popup>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#003366' }}>
                {stop.name}
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                Scheduled Departure: {stop.timing}
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                Route {selectedRoute.route_number} ({selectedRoute.route_name})
              </Typography>
            </Popup>
          </Marker>
        ))}

        {routePolyline.length > 1 && (
          <Polyline
            positions={routePolyline}
            pathOptions={{ color: '#003366', weight: 4, opacity: 0.8, dashArray: '6, 6' }}
          />
        )}

        {/* 4. Nearby Stops from Haversine Search */}
        {nearbyStops?.map((stop, idx) => (
          <Marker
            key={`nearby-${idx}`}
            position={[stop.latitude, stop.longitude]}
            icon={nearbyIcon}
          >
            <Popup>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: '#ea580c' }}>
                {stop.stop_name}
              </Typography>
              <Typography variant="body2">
                Route {stop.route_number} at {stop.timing}
              </Typography>
              <Typography variant="caption" sx={{ fontWeight: 600, color: '#ea580c' }}>
                Distance: {stop.distance_km} km
              </Typography>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </Box>
  );
}
