from crewai import Agent, LLM
from tools.calculator_tool import sip_calculator
from crewai.tools.base_tool import Tool
from config.settings import settings

def get_investment_agent():
    llm = LLM(
        model=f"ollama/{settings.OLLAMA_MODEL}",
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE,
        timeout=3600
    )
    return Agent(
        role="Investment Advisor",
        goal="""Analyze compound SIP calculations and wealth accumulation trends to provide customized asset 
                allocation recommendations.""",
        backstory="""You are a professional wealth advisor. You analyze compound interest SIP projections 
                     provided to you and recommend portfolio structures:
                     - Suggest balanced allocations between equity mutual funds, PPF, gold, or debt.
                     - Provide investment options for both short-term security and long-term wealth growth.""",
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=1
    )

investment_agent = get_investment_agent()