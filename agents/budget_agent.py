from crewai import Agent, LLM
from tools.calculator_tool import budget_calculator
from crewai.tools.base_tool import Tool
from config.settings import settings

def get_budget_agent():
    llm = LLM(
        model=f"ollama/{settings.OLLAMA_MODEL}",
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE,
        timeout=3600
    )
    return Agent(
        role="Budget Analyst",
        goal="""Analyze calculated budget inputs, evaluate spending behavior, savings rate, 
                and emergency fund needs to provide tailored budgeting recommendations.""",
        backstory="""You are a senior budgeting strategist. You take the budget calculation inputs 
                     (income, expenses, monthly surplus, savings rate, emergency fund target) 
                     provided to you and analyze them:
                     - Evaluate if the current savings rate is healthy (target is 20%+).
                     - Assess spending safety and monthly surplus.
                     - Recommend action steps to improve savings and emergency preparedness.""",
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=1
    )

budget_agent = get_budget_agent()