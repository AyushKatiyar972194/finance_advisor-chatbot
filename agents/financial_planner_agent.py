from crewai import Agent, LLM
from config.settings import settings

llm = LLM(
    model=f"ollama/{settings.OLLAMA_MODEL}",
    base_url=settings.OLLAMA_BASE_URL,
    temperature=settings.TEMPERATURE
)

financial_planner_agent = Agent(
    role="Chief Financial Planner",
    goal="""Consolidate calculations, budgets, investments, tax optimization, and debt payoff priority 
            into a final client-ready advisory report matching the requested JSON format.""",
    backstory="""You are a senior wealth management director. You synthesize raw numbers, analyses, 
                 and strategies from budgeting, tax, debt, and investment experts into a single structured report.
                 Your job is to formatting the report as a clean JSON object containing summary, recommendations, 
                 risks, and action plan, without any markdown delimiters.""",
    llm=llm,
    verbose=True,
    allow_delegation=False
)
