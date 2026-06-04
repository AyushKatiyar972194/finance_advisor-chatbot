from crewai import Agent, LLM
from tools.calculator_tool import tax_calculator
from crewai.tools.base_tool import Tool
from config.settings import settings

def get_tax_agent():
    llm = LLM(
        model=f"ollama/{settings.OLLAMA_MODEL}",
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.TEMPERATURE,
        timeout=3600
    )
    return Agent(
        role="Tax Consultant",
        goal="""Analyze tax estimations under Old and New regimes, compare their efficiencies, and identify legal tax-saving optimizations.""",
        backstory="""You are a chartered accountant. You take the Old vs New Tax Regime calculations 
                     provided to you and recommend regime choices:
                     - Compare tax liabilities under both regimes to recommend the most optimal one.
                     - Recommend specific deductions (Section 80C, 80D, ELSS, PPF, NPS) to reduce tax burden further.""",
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=1
    )

tax_agent = get_tax_agent()