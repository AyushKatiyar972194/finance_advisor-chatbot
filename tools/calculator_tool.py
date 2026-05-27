from crewai.tools import tool

@tool("Finance Calculator")
def finance_calculator(data: str) -> str:
    """
    Calculates EMI, SIP returns, savings goals.
    Input format: 'emi:principal=500000,rate=8.5,years=5'
    """
    try:
        if "emi" in data.lower():
            parts = data.split(",")
            principal = float(parts[0].split("=")[1])
            rate = float(parts[1].split("=")[1]) / 12 / 100
            months = int(parts[2].split("=")[1]) * 12
            
            emi = principal * rate * (1+rate)**months / ((1+rate)**months - 1)
            return f"Monthly EMI: ₹{emi:,.2f}"
        
        elif "sip" in data.lower():
            parts = data.split(",")
            monthly = float(parts[0].split("=")[1])
            rate = float(parts[1].split("=")[1]) / 12 / 100
            months = int(parts[2].split("=")[1]) * 12
            
            amount = monthly * ((1+rate)**months - 1) / rate * (1+rate)
            return f"SIP Maturity Amount: ₹{amount:,.2f}"
            
    except Exception as e:
        return f"Calculation error: {str(e)}. Ensure format is like 'emi:principal=50000,rate=8.5,years=5'."