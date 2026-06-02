import unittest
from unittest.mock import MagicMock, patch
from tools.calculator_tool import budget_calculator, sip_calculator, emi_calculator, tax_calculator
from services.chat_service import ChatService

class TestLangChainTools(unittest.TestCase):
    def test_budget_calculator_tool(self):
        # Test tool invocation directly using run()
        result = budget_calculator.invoke({"monthly_income": 50000.0, "monthly_expenses": 30000.0})
        self.assertIn("Monthly Income: INR 50,000.00", result)
        self.assertIn("Monthly Expenses: INR 30,000.00", result)
        self.assertIn("Monthly Surplus: INR 20,000.00", result)
        self.assertIn("Savings Rate: 40.00%", result)
        self.assertIn("Needs (50%): INR 25,000.00", result)
        self.assertIn("Wants (30%): INR 15,000.00", result)
        self.assertIn("Savings (20%): INR 10,000.00", result)
        self.assertIn("6-Month Emergency Fund Target: INR 180,000.00", result)

    def test_sip_calculator_tool(self):
        # Test tool invocation directly using run()
        result = sip_calculator.invoke({"monthly_investment": 5000.0, "expected_return_rate": 12.0, "years": 10})
        self.assertIn("Monthly SIP: INR 5,000.00", result)
        self.assertIn("Total Invested: INR 600,000.00", result)
        self.assertIn("Maturity Value: INR 1,161,695.38", result)
        self.assertIn("Wealth Gained: INR 561,695.38", result)

    def test_emi_calculator_tool(self):
        # Test tool invocation directly using run()
        result = emi_calculator.invoke({"principal": 500000.0, "annual_interest_rate": 8.5, "years": 5})
        self.assertIn("Loan Principal: INR 500,000.00", result)
        self.assertIn("Monthly EMI: INR 10,258.27", result)
        self.assertIn("Total Payment: INR 615,495.94", result)
        self.assertIn("Total Interest Payable: INR 115,495.94", result)

    def test_tax_calculator_tool(self):
        # Test tool invocation directly using run()
        result = tax_calculator.invoke({"annual_income": 1200000.0})
        self.assertIn("Annual Taxable Income: INR 1,200,000.00", result)
        self.assertIn("Tax New Regime: INR 78,750.00", result)
        self.assertIn("Tax Old Regime: INR 107,500.00", result)


class TestChatService(unittest.TestCase):
    @patch("workflows.finance_workflow.FinanceWorkflow")
    def test_chat_service_workflow_delegation(self, mock_workflow_class):
        mock_wf_instance = MagicMock()
        mock_wf_instance.run.return_value = "Mock Crew Output"
        mock_workflow_class.return_value = mock_wf_instance
        
        session_id = "test-session-routing"
        chat_service = ChatService()
        
        # Call chat method
        response = chat_service.chat(session_id, "I earn 50000 and spend 30000. Calculate my budget.")
        
        self.assertEqual(response, "Mock Crew Output")
        mock_wf_instance.run.assert_called_once_with("I earn 50000 and spend 30000. Calculate my budget.")
        
        # Verify history structure is saved
        history = chat_service.get_history(session_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "I earn 50000 and spend 30000. Calculate my budget.")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "Mock Crew Output")
