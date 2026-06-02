import unittest
from unittest.mock import MagicMock, patch
from workflows.finance_workflow import FinanceWorkflow

class TestFinanceWorkflow(unittest.TestCase):
    @patch("workflows.finance_workflow.Crew")
    @patch("urllib.request.urlopen")
    def test_workflow_run_success(self, mock_urlopen, mock_crew_class):
        # Mock connection check success (200 OK)
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        # Mock Crew execution
        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = "Mocked Crew Run Output"
        mock_crew_class.return_value = mock_crew

        # Instantiate workflow and execute
        workflow = FinanceWorkflow()
        result = workflow.run("I earn 50000 and spend 30000.")

        self.assertEqual(result, "Mocked Crew Run Output")
        mock_urlopen.assert_called_once()
        mock_crew_class.assert_called_once()

    @patch("urllib.request.urlopen")
    def test_workflow_run_unreachable_ollama(self, mock_urlopen):
        # Mock connection failure by raising Exception
        mock_urlopen.side_effect = Exception("Connection Refused")

        workflow = FinanceWorkflow()
        
        # Verify it raises a ConnectionError as expected when Ollama is down
        with self.assertRaises(ConnectionError):
            workflow.run("I earn 50000 and spend 30000.")
