import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from api import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("urllib.request.urlopen")
    def test_health_endpoint_healthy(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["ollama_connected"], True)
        self.assertIn("model", data)

    @patch("urllib.request.urlopen")
    def test_health_endpoint_unhealthy(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection Refused")
        
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "unhealthy")
        self.assertEqual(data["ollama_connected"], False)

    @patch("api.chat_service")
    def test_chat_endpoint(self, mock_chat_service):
        mock_chat_service.chat.return_value = "Mock response content from chat service"
        payload = {"session_id": "session-api-123", "message": "hello personal advisor"}
        response = self.client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["response"], "Mock response content from chat service")
        self.assertEqual(data["metadata"]["session_id"], "session-api-123")

    @patch("api.finance_workflow")
    def test_analysis_endpoint(self, mock_workflow):
        mock_workflow.run.return_value = "Mock financial report analysis output"
        payload = {"session_id": "session-api-123", "query": "income ₹50,000, spend ₹35,000"}
        response = self.client.post("/analysis", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["response"], "Mock financial report analysis output")
        self.assertEqual(data["metadata"]["session_id"], "session-api-123")
