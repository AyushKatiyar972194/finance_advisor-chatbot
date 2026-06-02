from crewai import Agent, LLM
from tools.calculator_tool import sip_calculator
from crewai.tools.base_tool import Tool
from config.settings import settings

llm = LLM(
    model=f"ollama/{settings.OLLAMA_MODEL}",
    base_url=settings.OLLAMA_BASE_URL,
    temperature=settings.TEMPERATURE
)

investment_agent = Agent(
    role="Investment Advisor",
    goal="""Analyze compound SIP calculator projections, evaluate wealth accumulation trends, 
            assess investment suitability for short/long term goals, and provide customized asset 
            allocation recommendations.""",
    backstory="""You are a professional wealth advisor. You analyze raw compounding calculations 
                 (monthly SIP, maturity amounts, tenure, interest) and execute the financial reasoning:
                 - Identify if the compounding returns meet target wealth projections.
                 - Formulate specific portfolio structures (e.g., allocations to equity mutual funds, PPF, gold, or debt).
                 - Outline short-term vs long-term investment suitability.""",
    tools=[Tool.from_langchain(sip_calculator)],
    llm=llm,
    verbose=True,
    allow_delegation=False
)