from crewai import Agent, LLM
from tools.calculator_tool import emi_calculator
from crewai.tools.base_tool import Tool
from config.settings import settings

llm = LLM(
    model=f"ollama/{settings.OLLAMA_MODEL}",
    base_url=settings.OLLAMA_BASE_URL,
    temperature=settings.TEMPERATURE
)

debt_agent = Agent(
    role="Debt Management Expert",
    goal="""Analyze raw loan EMI calculations, evaluate outstanding liability burden, 
            identify debt default/repayment risks, and formulate prioritized payoff strategies.""",
    backstory="""You are a professional debt management consultant. You inspect raw numbers 
                 (principal, interest rates, tenure, EMI amounts) and perform the advisory logic:
                 - Evaluate if the monthly EMI relative to income represents high debt burden risk.
                 - Formulate customized payoff strategies (avalanche vs snowball priority).
                 - Outline interest-minimization advice for loans.""",
    tools=[Tool.from_langchain(emi_calculator)],
    llm=llm,
    verbose=True,
    allow_delegation=False
)