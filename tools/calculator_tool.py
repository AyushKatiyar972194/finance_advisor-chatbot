from langchain.tools import tool
from typing import Optional
import logging
import math

logger = logging.getLogger(__name__)

@tool("budget_calculator")
def budget_calculator(monthly_income: Optional[float] = None, monthly_expenses: Optional[float] = None) -> str:
    """
    Calculates 50-30-20 budget splits, surplus, savings rate, and 6-month emergency fund target size.
    Input parameters:
      monthly_income: Total monthly income as a number. Can be null/None.
      monthly_expenses: Total monthly expenses as a number. Can be null/None.
    """
    try:
        logger.info(f"Budget Calculator Tool invoked: income={monthly_income}, expenses={monthly_expenses}")
        if monthly_income is None or monthly_expenses is None:
            missing = []
            if monthly_income is None: missing.append("monthly_income")
            if monthly_expenses is None: missing.append("monthly_expenses")
            return f"Error: Missing required inputs for Budget calculation. Required: {', '.join(missing)}."

        if monthly_income <= 0:
            return "Error: Income must be greater than zero."

        surplus = monthly_income - monthly_expenses
        savings_rate = (surplus / monthly_income) * 100 if monthly_income > 0 else 0
        needs_50 = monthly_income * 0.50
        wants_30 = monthly_income * 0.30
        savings_20 = monthly_income * 0.20
        emergency_fund = monthly_expenses * 6

        return (
            f"Monthly Income: INR {monthly_income:,.2f}\n"
            f"Monthly Expenses: INR {monthly_expenses:,.2f}\n"
            f"Monthly Surplus: INR {surplus:,.2f}\n"
            f"Savings Rate: {savings_rate:.2f}%\n"
            f"50-30-20 Allocation Plan:\n"
            f"- Needs (50%): INR {needs_50:,.2f}\n"
            f"- Wants (30%): INR {wants_30:,.2f}\n"
            f"- Savings (20%): INR {savings_20:,.2f}\n"
            f"6-Month Emergency Fund Target: INR {emergency_fund:,.2f}"
        )
    except Exception as e:
        logger.error(f"Error in budget calculator tool: {e}")
        return f"Budget calculation error: {str(e)}"

@tool("sip_calculator")
def sip_calculator(monthly_investment: Optional[float] = None, expected_return_rate: Optional[float] = None, years: Optional[int] = None) -> str:
    """
    Calculates SIP total invested amount, estimated compound maturity returns, and wealth gained.
    Input parameters:
      monthly_investment: Monthly SIP investment amount as a number. Can be null/None.
      expected_return_rate: Annual expected return rate as percentage (e.g. 12.0 for 12%). Can be null/None.
      years: Investment duration in years as a number. Can be null/None.
    """
    try:
        logger.info(f"SIP Calculator Tool invoked: monthly={monthly_investment}, rate={expected_return_rate}, years={years}")
        if monthly_investment is None or expected_return_rate is None or years is None:
            missing = []
            if monthly_investment is None: missing.append("monthly_investment")
            if expected_return_rate is None: missing.append("expected_return_rate")
            if years is None: missing.append("years")
            return f"Error: Missing required inputs for SIP calculation. Required: {', '.join(missing)}."

        rate_monthly = expected_return_rate / 12 / 100
        months = years * 12
        total_invested = monthly_investment * months
        # Future Value formula for SIP (annuity due)
        maturity_value = monthly_investment * (((1 + rate_monthly) ** months - 1) / rate_monthly) * (1 + rate_monthly)
        estimated_returns = maturity_value - total_invested

        return (
            f"Monthly SIP: INR {monthly_investment:,.2f}\n"
            f"Tenure: {years} years ({months} months)\n"
            f"Expected Return Rate: {expected_return_rate:.2f}%\n"
            f"Total Invested: INR {total_invested:,.2f}\n"
            f"Maturity Value: INR {maturity_value:,.2f}\n"
            f"Wealth Gained: INR {estimated_returns:,.2f}"
        )
    except Exception as e:
        logger.error(f"Error in SIP calculator tool: {e}")
        return f"SIP calculation error: {str(e)}"

@tool("emi_calculator")
def emi_calculator(principal: Optional[float] = None, annual_interest_rate: Optional[float] = None, years: Optional[int] = None) -> str:
    """
    Calculates monthly EMI principal installments, total payment, and total interest payable for a loan.
    Input parameters:
      principal: The loan principal amount as a number. Can be null/None.
      annual_interest_rate: The annual interest rate as percentage (e.g. 8.5 for 8.5%). Can be null/None.
      years: The loan tenure in years as a number. Can be null/None.
    """
    try:
        logger.info(f"EMI Calculator Tool invoked: principal={principal}, rate={annual_interest_rate}, years={years}")
        if principal is None or annual_interest_rate is None or years is None:
            missing = []
            if principal is None: missing.append("principal")
            if annual_interest_rate is None: missing.append("annual_interest_rate")
            if years is None: missing.append("years")
            return f"Error: Missing required inputs for EMI calculation. Required: {', '.join(missing)}."

        rate_monthly = annual_interest_rate / 12 / 100
        months = years * 12
        # Standard EMI Formula: P * r * (1+r)^n / ((1+r)^n - 1)
        emi = principal * rate_monthly * (1 + rate_monthly) ** months / ((1 + rate_monthly) ** months - 1)
        total_payment = emi * months
        total_interest = total_payment - principal

        return (
            f"Loan Principal: INR {principal:,.2f}\n"
            f"Tenure: {years} years ({months} months)\n"
            f"Annual Interest Rate: {annual_interest_rate:.2f}%\n"
            f"Monthly EMI: INR {emi:,.2f}\n"
            f"Total Payment: INR {total_payment:,.2f}\n"
            f"Total Interest Payable: INR {total_interest:,.2f}"
        )
    except Exception as e:
        logger.error(f"Error in EMI calculator tool: {e}")
        return f"EMI calculation error: {str(e)}"

@tool("tax_calculator")
def tax_calculator(annual_income: Optional[float] = None) -> str:
    """
    Estimates income tax liability under Old and New regimes for a given annual taxable income.
    Input parameters:
      annual_income: Total annual taxable income as a number. Can be null/None.
    """
    try:
        logger.info(f"Tax Calculator Tool invoked: annual_income={annual_income}")
        if annual_income is None:
            return "Error: Missing required inputs for Tax calculation. Required: annual_income."

        # New Tax Regime Calculation (FY 2024-25 / AY 2025-26)
        net_new = max(0.0, annual_income - 75000.0)
        tax_new = 0.0
        if net_new > 700000.0:
            temp = net_new
            if temp > 1500000.0:
                tax_new += (temp - 1500000.0) * 0.30
                temp = 1500000.0
            if temp > 1200000.0:
                tax_new += (temp - 1200000.0) * 0.20
                temp = 1200000.0
            if temp > 900000.0:
                tax_new += (temp - 900000.0) * 0.15
                temp = 900000.0
            if temp > 600000.0:
                tax_new += (temp - 600000.0) * 0.10
                temp = 600000.0
            if temp > 300000.0:
                tax_new += (temp - 300000.0) * 0.05
                temp = 300000.0

        # Old Tax Regime Calculation
        # Std Ded 50k + Sec 80C 1.5L + Sec 80D 25k = 225,000 INR deductions
        deductions_old = 50000.0 + 150000.0 + 25000.0
        net_old = max(0.0, annual_income - deductions_old)
        tax_old = 0.0
        if net_old > 500000.0:
            temp = net_old
            if temp > 1000000.0:
                tax_old += (temp - 1000000.0) * 0.30
                temp = 1000000.0
            if temp > 500000.0:
                tax_old += (temp - 500000.0) * 0.20
                temp = 500000.0
            if temp > 250000.0:
                tax_old += (temp - 250000.0) * 0.05
                temp = 250000.0

        return (
            f"Annual Taxable Income: INR {annual_income:,.2f}\n"
            f"Tax New Regime: INR {tax_new:,.2f}\n"
            f"Tax Old Regime: INR {tax_old:,.2f}"
        )
    except Exception as e:
        logger.error(f"Error in tax calculator tool: {e}")
        return f"Tax calculation error: {str(e)}"