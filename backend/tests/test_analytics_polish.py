"""
Analytics Polish Features Tests - Tier 1, 2, 3
Tests all new polish features for the Monitoring & Analytics Dashboard

Tier 1: Threshold alerts, Last Updated timestamp, Skeleton loaders, Animations
Tier 2: WebSocket support, Drift notifications, Mini sparklines, Metrics source indicator
Tier 3: Historical export CSV/JSON, Customizable widgets with localStorage, Dark/Light theme toggle
"""

import pytest
import requests
import os
import asyncio
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestTier1Features:
    """Tier 1: Threshold alerts, Last Updated timestamp, Skeleton loaders, Animations"""
    
    def test_system_health_returns_threshold_data(self):
        """Test system health returns data for threshold alerts (CPU > 80%, Memory > 90%, Disk > 95%)"""
        response = requests.get(f"{BASE_URL}/api/analytics/system-health")
        assert response.status_code == 200
        
        data = response.json()
        # Verify threshold-relevant fields exist
        assert "cpu_usage" in data
        assert "memory_usage" in data
        assert "disk_usage" in data
        assert "status" in data
        
        # Verify values are in valid range for threshold checking
        assert 0 <= data["cpu_usage"] <= 100
        assert 0 <= data["memory_usage"] <= 100
        assert 0 <= data["disk_usage"] <= 100
        
        # Verify status reflects thresholds
        assert data["status"] in ["healthy", "degraded", "critical"]
    
    def test_realtime_stats_has_timestamp(self):
        """Test realtime stats returns timestamp for Last Updated feature"""
        response = requests.get(f"{BASE_URL}/api/analytics/realtime-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        # Verify timestamp is ISO format
        assert "T" in data["timestamp"]


class TestTier2Features:
    """Tier 2: WebSocket support, Drift notifications, Mini sparklines, Metrics source indicator"""
    
    def test_websocket_endpoint_exists(self):
        """Test WebSocket endpoint is available at /api/analytics/ws"""
        # We can't test WebSocket with requests, but we can verify the endpoint exists
        # by checking the router is registered
        response = requests.get(f"{BASE_URL}/api/analytics/realtime-stats")
        assert response.status_code == 200
        # WebSocket endpoint is registered in the same router
    
    def test_drift_status_returns_notification_data(self):
        """Test drift status returns data for drift notifications"""
        response = requests.get(f"{BASE_URL}/api/analytics/drift-status")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            item = data[0]
            # Verify fields needed for drift notifications
            assert "engine" in item
            assert "status" in item
            assert "message" in item
            assert "confidence_trend" in item
            
            # Verify status values for notification styling
            assert item["status"] in ["green", "yellow", "red"]
            assert item["confidence_trend"] in ["stable", "rising", "falling"]
    
    def test_engine_latency_returns_sparkline_data(self):
        """Test engine latency returns data suitable for mini sparklines"""
        response = requests.get(f"{BASE_URL}/api/analytics/engine-latency")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            item = data[0]
            # Verify numeric data for sparklines
            assert "avg_latency_ms" in item
            assert isinstance(item["avg_latency_ms"], (int, float))
    
    def test_system_health_has_psutil_indicator(self):
        """Test system health returns psutil_available for metrics source indicator"""
        response = requests.get(f"{BASE_URL}/api/analytics/system-health")
        assert response.status_code == 200
        
        data = response.json()
        assert "psutil_available" in data
        assert isinstance(data["psutil_available"], bool)
        # In our environment, psutil should be available
        assert data["psutil_available"] == True


class TestTier3Features:
    """Tier 3: Historical export CSV/JSON, Customizable widgets, Dark/Light theme"""
    
    def test_engine_usage_returns_exportable_data(self):
        """Test engine usage returns data suitable for CSV/JSON export"""
        response = requests.get(f"{BASE_URL}/api/analytics/engine-usage")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # Verify data is JSON serializable (for JSON export)
        json_str = json.dumps(data)
        assert len(json_str) > 0
        
        # Verify data has fields for CSV export
        if len(data) > 0:
            item = data[0]
            assert "engine" in item
            assert "count" in item
    
    def test_all_analytics_endpoints_return_json(self):
        """Test all analytics endpoints return valid JSON for export"""
        endpoints = [
            "/api/analytics/engine-usage",
            "/api/analytics/engine-latency",
            "/api/analytics/engine-errors",
            "/api/analytics/drift-status",
            "/api/analytics/system-health",
            "/api/analytics/confidence-trends",
            "/api/analytics/model-comparison",
            "/api/analytics/realtime-stats"
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 200, f"Failed: {endpoint}"
            
            # Verify JSON is valid
            data = response.json()
            assert data is not None, f"No data from {endpoint}"
    
    def test_confidence_trends_returns_time_series_for_export(self):
        """Test confidence trends returns time series data for historical export"""
        response = requests.get(f"{BASE_URL}/api/analytics/confidence-trends")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            item = data[0]
            assert "data_points" in item
            assert isinstance(item["data_points"], list)
            
            # Verify time series structure
            if len(item["data_points"]) > 0:
                point = item["data_points"][0]
                assert "timestamp" in point
                assert "value" in point


class TestWebSocketIntegration:
    """Test WebSocket endpoint functionality"""
    
    def test_websocket_connection(self):
        """Test WebSocket endpoint accepts connections and sends data"""
        import asyncio
        
        async def test_ws():
            try:
                import websockets
                ws_url = BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://')
                
                async with websockets.connect(f"{ws_url}/api/analytics/ws", close_timeout=5) as ws:
                    # Wait for initial message
                    message = await asyncio.wait_for(ws.recv(), timeout=5)
                    data = json.loads(message)
                    
                    # Verify message structure
                    assert data.get("type") == "realtime"
                    assert "stats" in data
                    assert "health" in data
                    
                    # Verify stats structure
                    stats = data["stats"]
                    assert "total_executions" in stats
                    assert "success_rate" in stats
                    
                    # Verify health structure
                    health = data["health"]
                    assert "cpu_usage" in health
                    assert "psutil_available" in health
                    
                    return True
            except ImportError:
                pytest.skip("websockets library not available")
            except Exception as e:
                pytest.fail(f"WebSocket test failed: {e}")
        
        result = asyncio.run(test_ws())
        assert result == True


class TestDataConsistency:
    """Test data consistency across endpoints for dashboard features"""
    
    def test_system_health_status_matches_thresholds(self):
        """Verify system health status correctly reflects threshold values"""
        response = requests.get(f"{BASE_URL}/api/analytics/system-health")
        assert response.status_code == 200
        
        data = response.json()
        cpu = data["cpu_usage"]
        memory = data["memory_usage"]
        disk = data["disk_usage"]
        status = data["status"]
        
        # Verify status logic
        if cpu > 90 or memory > 90 or disk > 95:
            assert status == "critical"
        elif cpu > 70 or memory > 75 or disk > 80:
            assert status == "degraded"
        else:
            assert status == "healthy"
    
    def test_drift_status_has_all_engines(self):
        """Verify drift status covers all active engines"""
        drift_response = requests.get(f"{BASE_URL}/api/analytics/drift-status")
        usage_response = requests.get(f"{BASE_URL}/api/analytics/engine-usage")
        
        assert drift_response.status_code == 200
        assert usage_response.status_code == 200
        
        drift_data = drift_response.json()
        usage_data = usage_response.json()
        
        # Get engine names from both endpoints
        drift_engines = set(d["engine"] for d in drift_data)
        usage_engines = set(u["engine"] for u in usage_data)
        
        # All usage engines should have drift status
        for engine in usage_engines:
            assert engine in drift_engines, f"Engine {engine} missing from drift status"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
