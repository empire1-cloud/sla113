# Analytics Dashboard - Documentation

## Overview
The Monitoring & Analytics Dashboard provides real-time visibility into the Hybrid Intelligence system's performance, AI quality, and system health with premium polish features.

## System Requirements

### psutil Dependency
The analytics dashboard uses **psutil** for real system metrics (CPU, RAM, Disk, Load Average).

**Important:** `psutil` must be installed globally on the VPS environment:
```bash
pip install psutil
```

If psutil is unavailable, the dashboard will automatically fall back to mock data and display a warning indicator.

## Features

### Tier 1 — Must-Have Polish

#### 1. Threshold-Based Alerts
- **CPU > 80%**: Critical alert (red)
- **Memory > 90%**: Critical alert (red)  
- **Disk > 95%**: Critical alert (red)
- **Drift score degraded**: Warning/Critical based on severity
- Toast notifications appear for critical alerts
- Alert banner displays count of warnings/critical issues

#### 2. Last Updated Timestamp
- Displays exact time of last data refresh
- Updates automatically every 5 seconds

#### 3. Skeleton Loaders
- Animated shimmer effect during initial load
- Shows for all chart and metric cards

#### 4. Smooth Animations
- Gauge values animate smoothly on change
- Cards have hover lift effect
- Flash animations for value increases/decreases

### Tier 2 — Premium Polish

#### 5. WebSocket Support
- Real-time updates via WebSocket connection
- URL: `wss://{domain}/api/analytics/ws`
- Updates every 1 second when connected
- Automatic fallback to 5-second polling if connection fails
- Toast notification on connection established

#### 6. Drift Event Notifications
- Visual highlighting with pulse animation
- Toast alerts for new drift events
- Red cards have glowing pulse effect

#### 7. Mini Sparklines
- Shows recent usage/latency trends per engine
- Located below the latency chart
- Real-time data collected from API calls

#### 8. Metrics Source Indicator
- Shows "LIVE" (green) when WebSocket connected
- Shows "POLLING" (blue) when using fallback
- System Health tab shows connection type

### Tier 3 — Luxury Polish

#### 9. Historical Export
- **JSON Export**: Full analytics data with all metrics
- **CSV Export**: Tabular format for spreadsheets
- Downloads include: engine usage, latency, errors, drift, system metrics

#### 10. Customizable Widgets
- Show/hide any dashboard section
- Preferences saved to localStorage
- Persists across browser sessions

#### 11. Dark/Light Theme Toggle
- Default: Dark mode (operator-grade aesthetic)
- Smooth transition between themes
- Preference saved to localStorage

## Real-Time Updates
- WebSocket: ~1 second updates when connected
- Polling fallback: 5 second interval
- LIVE indicator shows connection status
- Last update timestamp displayed in header

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/analytics/engine-usage` | Request counts per engine |
| `GET /api/analytics/engine-latency` | Latency metrics (avg, min, max, p95) |
| `GET /api/analytics/engine-errors` | Error rates and severity |
| `GET /api/analytics/drift-status` | AI drift detection alerts |
| `GET /api/analytics/system-health` | CPU, memory, disk metrics |
| `GET /api/analytics/pipeline-graph` | Active pipeline visualization |
| `GET /api/analytics/confidence-trends` | 12-hour confidence time series |
| `GET /api/analytics/model-comparison` | LLM model performance comparison |
| `GET /api/analytics/realtime-stats` | Quick stats for polling |
| `WS /api/analytics/ws` | WebSocket for real-time updates |

### WebSocket Message Format
```json
{
  "type": "realtime",
  "stats": {
    "timestamp": "2025-02-09T04:20:00Z",
    "total_executions": 5,
    "success_rate": 100,
    ...
  },
  "health": {
    "cpu_usage": 15.2,
    "memory_usage": 54.8,
    ...
  }
}
```

## localStorage Keys
- `analytics-theme`: "dark" | "light"
- `analytics-widgets`: JSON object with widget visibility

## File Structure
```
/app/backend/routers/engines/analytics.py  # Backend endpoints + WebSocket
/app/frontend/src/pages/AnalyticsPage.jsx  # React component with all features
/app/frontend/src/App.css                  # Dashboard styles + animations
```

## Dependencies
- **Backend**: FastAPI, Pydantic, psutil (optional)
- **Frontend**: React, Recharts, Axios, Sonner (toasts)

## Performance Notes
- Caching prevents database/log file hammering (5s TTL)
- WebSocket sends compressed updates
- Animations use CSS transforms (GPU-accelerated)
- Skeleton loaders prevent layout shift
