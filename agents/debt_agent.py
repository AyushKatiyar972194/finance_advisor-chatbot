from crewai import Agent, LLM
from tools.calculator_tool import emi_calculator
from crewai.tools.base_tool import Tool
from config.settings import settings

def get_debt_agent():
    llm = LLM(
        model=f"ollama/{settings.OLLAMA_MODEL}",
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE,
        timeout=3600
    )
    return Agent(
        role="Debt Management Expert",
        goal="""Analyze loan EMI calculations and outstanding liabilities to formulate prioritized debt payoff strategies.""",
        backstory="""You are a professional debt management consultant. You inspect loan and EMI calculations 
                     provided to you and recommend payoff strategies:
                     - Recommend prioritized payoff strategies (debt avalanche vs debt snowball).
                     - Advise on loan pre-payments or restructuring to minimize interest payable.
                     - If no debts are present, suggest how to maintain a debt-free profile.""",
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=1
    )

debt_agent = get_debt_agent()