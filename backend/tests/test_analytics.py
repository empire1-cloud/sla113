"""
Analytics API Tests - Monitoring & Dashboard endpoints
Tests all 9 analytics endpoints for the Monitoring & Analytics Dashboard
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAnalyticsEndpoints:
    """Test all analytics API endpoints"""
    
    def test_realtime_stats_returns_valid_data(self):
        """Test /api/analytics/realtime-stats returns valid structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/realtime-stats")
        assert response.status_code == 200
        
        data = response.json()
        # Verify required fields exist
        assert "timestamp" in data
        assert "total_executions" in data
        assert "success_rate" in data
        assert "avg_duration_ms" in data
        assert "error_count" in data
        assert "recent_5min" in data
        assert "active_engines" in data
        assert "system" in data
        
        # Verify data types
        assert isinstance(data["total_executions"], int)
        assert isinstance(data["success_rate"], (int, float))
        assert isinstance(data["avg_duration_ms"], (int, float))
        
        # Verify system sub-object
        assert "cpu" in data["system"]
        assert "memory" in data["system"]
        assert "status" in data["system"]
        assert "psutil_available" in data["system"]
        
        # Verify psutil is available in realtime-stats
        assert data["system"]["psutil_available"] == True, "psutil should be available"
        
    def test_engine_usage_returns_array(self):
        """Test /api/analytics/engine-usage returns array of engine usage"""
        response = requests.get(f"{BASE_URL}/api/analytics/engine-usage")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        # If data exists, verify structure
        if len(data) > 0:
            item = data[0]
            assert "engine" in item
            assert "count" in item
            assert "display_name" in item
            assert isinstance(item["count"], int)
            
    def test_engine_latency_returns_array(self):
        """Test /api/analytics/engine-latency returns latency metrics"""
        response = requests.get(f"{BASE_URL}/api/analytics/engine-latency")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            item = data[0]
            assert "engine" in item
            assert "avg_latency_ms" in item
            assert "min_latency_ms" in item
            assert "max_latency_ms" in item
            assert "p95_latency_ms" in item
            assert "display_name" in item
            
    def test_engine_errors_returns_array(self):
        """Test /api/analytics/engine-errors returns error rates"""
        response = requests.get(f"{BASE_URL}/api/analytics/engine-errors")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            item = data[0]
            assert "engine" in item
            assert "total_calls" in item
            assert "error_count" in item
            assert "error_rate" in item
            assert "severity" in item
            assert item["severity"] in ["low", "medium", "high"]
            
    def test_drift_status_returns_array(self):
        """Test /api/analytics/drift-status returns drift alerts"""
        response = requests.get(f"{BASE_URL}/api/analytics/drift-status")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            item = data[0]
            assert "engine" in item
            assert "status" in item
            assert "confidence_trend" in item
            assert "last_check" in item
            assert "message" in item
            assert item["status"] in ["green", "yellow", "red"]
            assert item["confidence_trend"] in ["stable", "rising", "falling"]
            
    def test_system_health_returns_metrics(self):
        """Test /api/analytics/system-health returns real psutil metrics"""
        response = requests.get(f"{BASE_URL}/api/analytics/system-health")
        assert response.status_code == 200
        
        data = response.json()
        # Basic fields
        assert "cpu_usage" in data
        assert "memory_usage" in data
        assert "disk_usage" in data
        assert "active_connections" in data
        assert "uptime_hours" in data
        assert "status" in data
        
        # NEW psutil fields
        assert "psutil_available" in data
        assert "memory_total_gb" in data
        assert "memory_used_gb" in data
        assert "disk_total_gb" in data
        assert "disk_used_gb" in data
        assert "load_average" in data
        
        # Verify psutil is available (real metrics)
        assert data["psutil_available"] == True, "psutil should be available for real metrics"
        
        # Verify ranges
        assert 0 <= data["cpu_usage"] <= 100
        assert 0 <= data["memory_usage"] <= 100
        assert 0 <= data["disk_usage"] <= 100
        assert data["status"] in ["healthy", "degraded", "critical"]
        
        # Verify memory details
        assert isinstance(data["memory_total_gb"], (int, float))
        assert isinstance(data["memory_used_gb"], (int, float))
        assert data["memory_total_gb"] > 0
        assert data["memory_used_gb"] >= 0
        assert data["memory_used_gb"] <= data["memory_total_gb"]
        
        # Verify disk details
        assert isinstance(data["disk_total_gb"], (int, float))
        assert isinstance(data["disk_used_gb"], (int, float))
        assert data["disk_total_gb"] > 0
        assert data["disk_used_gb"] >= 0
        assert data["disk_used_gb"] <= data["disk_total_gb"]
        
        # Verify load average (array with 3 values: 1, 5, 15 min)
        assert isinstance(data["load_average"], list)
        assert len(data["load_average"]) == 3
        for load_val in data["load_average"]:
            assert isinstance(load_val, (int, float))
            assert load_val >= 0
        
    def test_pipeline_graph_returns_nodes_and_edges(self):
        """Test /api/analytics/pipeline-graph returns graph structure"""
        response = requests.get(f"{BASE_URL}/api/analytics/pipeline-graph")
        assert response.status_code == 200
        
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert "active_pipelines" in data
        assert "queue_length" in data
        assert "throughput_per_minute" in data
        
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)
        
        # Verify node structure
        if len(data["nodes"]) > 0:
            node = data["nodes"][0]
            assert "id" in node
            assert "name" in node
            assert "type" in node
            assert "status" in node
            
    def test_confidence_trends_returns_time_series(self):
        """Test /api/analytics/confidence-trends returns time series data"""
        response = requests.get(f"{BASE_URL}/api/analytics/confidence-trends")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        
        if len(data) > 0:
            item = data[0]
            assert "engine" in item
            assert "data_points" in item
            assert "current_confidence" in item
            assert "trend" in item
            
            # Verify data points structure
            if len(item["data_points"]) > 0:
                point = item["data_points"][0]
                assert "timestamp" in point
                assert "value" in point
                assert 0 <= point["value"] <= 1  # Confidence should be 0-1
                
    def test_model_comparison_returns_models(self):
        """Test /api/analytics/model-comparison returns model data"""
        response = requests.get(f"{BASE_URL}/api/analytics/model-comparison")
        assert response.status_code == 200
        
        data = response.json()
        assert "models" in data
        assert isinstance(data["models"], list)
        assert len(data["models"]) >= 3  # Should have at least 3 models
        
        # Verify model structure
        model = data["models"][0]
        assert "name" in model
        assert "provider" in model
        assert "version" in model
        assert "avg_latency_ms" in model
        assert "tokens_per_second" in model
        assert "cost_per_1k_tokens" in model
        assert "primary_use" in model


class TestAnalyticsDataIntegrity:
    """Test data integrity and consistency across endpoints"""
    
    def test_realtime_stats_matches_engine_usage(self):
        """Verify realtime stats active_engines matches engine-usage count"""
        stats_response = requests.get(f"{BASE_URL}/api/analytics/realtime-stats")
        usage_response = requests.get(f"{BASE_URL}/api/analytics/engine-usage")
        
        assert stats_response.status_code == 200
        assert usage_response.status_code == 200
        
        stats = stats_response.json()
        usage = usage_response.json()
        
        # Active engines should match unique engines in usage
        assert stats["active_engines"] == len(usage)
        
    def test_error_rates_are_consistent(self):
        """Verify error rates are calculated correctly"""
        response = requests.get(f"{BASE_URL}/api/analytics/engine-errors")
        assert response.status_code == 200
        
        data = response.json()
        for item in data:
            if item["total_calls"] > 0:
                expected_rate = (item["error_count"] / item["total_calls"]) * 100
                assert abs(item["error_rate"] - expected_rate) < 0.1  # Allow small float diff


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
