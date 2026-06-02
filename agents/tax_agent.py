from crewai import Agent, LLM
from tools.calculator_tool import tax_calculator
from crewai.tools.base_tool import Tool
from config.settings import settings

llm = LLM(
    model=f"ollama/{settings.OLLAMA_MODEL}",
    base_url=settings.OLLAMA_BASE_URL,
    temperature=settings.TEMPERATURE
)

tax_agent = Agent(
    role="Tax Consultant",
    goal="""Analyze raw old and new regime tax estimations, compare regime tax efficiency, 
            determine the optimal regime choice, and identify legal tax-saving optimizations.""",
    backstory="""You are a chartered accountant. You take raw tax values (old regime tax, new regime tax, income) 
                 and execute the tax planning logic:
                 - Compare the liabilities and determine which regime is the optimal choice for this client.
                 - Formulate specific legal tax deductions to optimize savings (e.g. suggesting Section 80C, 80D, 
                   PPF, NPS, or Health Insurance thresholds if the Old Regime is beneficial).""",
    tools=[Tool.from_langchain(tax_calculator)],
    llm=llm,
    verbose=True,
    allow_delegation=False
)