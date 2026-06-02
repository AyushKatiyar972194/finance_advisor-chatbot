from crewai import Agent, LLM
from tools.calculator_tool import budget_calculator
from crewai.tools.base_tool import Tool
from config.settings import settings

llm = LLM(
    model=f"ollama/{settings.OLLAMA_MODEL}",
    base_url=settings.OLLAMA_BASE_URL,
    temperature=settings.TEMPERATURE
)

budget_agent = Agent(
    role="Budget Analyst",
    goal="""Analyze raw budget calculator outputs, evaluate spending behaviour, 
            assess savings discipline, identify emergency preparedness risks, and provide 
            tailored budgeting recommendations.""",
    backstory="""You are a senior budgeting strategist. You take raw mathematical numbers 
                 (income, expenses, surplus, savings rate, emergency fund target) and perform 
                 the logical analysis:
                 - Evaluate if the current savings rate is healthy (e.g., check if it is below the target 20% threshold).
                 - Assess if monthly expenses leave enough surplus to cover basic security.
                 - Recommend explicit spending behaviors and savings adjustments.
                 - Advise on how many months it will take to complete the emergency fund given the monthly surplus.""",
    tools=[Tool.from_langchain(budget_calculator)],
    llm=llm,
    verbose=True,
    allow_delegation=False
)