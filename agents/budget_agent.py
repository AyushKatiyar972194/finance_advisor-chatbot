from crewai import Agent
from tools.calculator_tool import finance_calculator

def create_budget_agent(llm):
    return Agent(
        role="Budget Analyst",
        goal="""Analyze user's income and expenses.
                Create a practical monthly budget plan.
                Apply 50-30-20 rule for Indian households.""",
        backstory="""You are an expert budget analyst with 
                     10 years of experience helping Indian 
                     middle-class families manage finances.
                     You know Indian expenses well — rent, 
                     groceries, school fees, EMIs etc.""",
        tools=[finance_calculator],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )