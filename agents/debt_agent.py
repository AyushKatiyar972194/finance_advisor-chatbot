from crewai import Agent
from tools.calculator_tool import finance_calculator

def create_debt_agent(llm):
    return Agent(
        role="Debt Management Expert",
        goal="""Help users manage and eliminate debt smartly.
                Calculate EMIs and suggest debt payoff strategies.""",
        backstory="""You are a debt counselor who has helped 
                     thousands of Indians get out of debt.
                     Expert in: home loans, personal loans, 
                     credit card debt, and EMI management.
                     You use avalanche and snowball methods.""",
        tools=[finance_calculator],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )