from crewai import Crew, Task, Process
from agents.budget_agent import create_budget_agent
from agents.investment_agent import create_investment_agent
from agents.tax_agent import create_tax_agent
from agents.debt_agent import create_debt_agent
from gemini_model import get_gemini_model
from ollama_model import get_ollama_model

def run_finance_crew(user_query: str, use_ollama: bool = False) -> str:
    
    # Choose model
    if use_ollama:
        llm = get_ollama_model()
    else:
        llm = get_gemini_model()
    
    # Create agents
    budget_agent   = create_budget_agent(llm)
    invest_agent   = create_investment_agent(llm)
    tax_agent      = create_tax_agent(llm)
    debt_agent     = create_debt_agent(llm)
    
    # Create tasks
    budget_task = Task(
        description=f"""
        Analyze this financial situation and create budget plan:
        {user_query}
        
        Provide:
        1. Income breakdown
        2. Expense categories
        3. Monthly budget plan
        4. Savings target
        """,
        agent=budget_agent,
        expected_output="Detailed budget analysis with numbers"
    )
    
    investment_task = Task(
        description=f"""
        Based on the budget analysis, recommend investments for:
        {user_query}
        
        Provide:
        1. Short term investments (0-1 year)
        2. Long term investments (5+ years)
        3. Specific amounts to invest
        4. Expected returns
        """,
        agent=invest_agent,
        expected_output="Investment plan with specific recommendations"
    )
    
    tax_task = Task(
        description=f"""
        Suggest tax saving strategies for:
        {user_query}
        
        Provide:
        1. Available deductions
        2. Recommended tax saving instruments
        3. Estimated tax saved
        """,
        agent=tax_agent,
        expected_output="Tax saving plan with deductions"
    )
    
    debt_task = Task(
        description=f"""
        If there are any loans or debts in:
        {user_query}
        
        Provide:
        1. EMI calculations
        2. Debt payoff strategy
        3. Priority order for debt repayment
        """,
        agent=debt_agent,
        expected_output="Debt management strategy"
    )
    
    # Assemble crew
    crew = Crew(
        agents=[budget_agent, invest_agent, tax_agent, debt_agent],
        tasks=[budget_task, investment_task, tax_task, debt_task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    return str(result)