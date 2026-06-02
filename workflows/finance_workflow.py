import logging
import urllib.request
import json
from crewai import Crew, Task, Process
from config.settings import settings
from agents.budget_agent import budget_agent
from agents.investment_agent import investment_agent
from agents.debt_agent import debt_agent
from agents.tax_agent import tax_agent
from agents.financial_planner_agent import financial_planner_agent

logger = logging.getLogger(__name__)

class FinanceWorkflow:
    def __init__(self):
        pass

    def run(self, user_query: str) -> str:
        logger.info(f"Initiating Finance Workflow Crew with user query: {user_query}")
        
        # Verify Ollama server connectivity at run time
        try:
            url = f"{settings.OLLAMA_BASE_URL}/api/tags"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as response:
                if response.status != 200:
                    raise ConnectionError()
        except Exception:
            err_msg = (
                "Ollama service is currently unavailable or unreachable. "
                "Ensure Ollama is running and that the configured model is pulled."
            )
            logger.error(err_msg)
            raise ConnectionError(err_msg)

        # 1. Budget Task
        budget_task = Task(
            description=f"""
            Analyze the user's financial details from the query: '{user_query}'
            
            Identify if income and expenses are provided. If present, run the 'Budget Calculator' tool 
            with the extracted income and expenses. Use the outputs to determine the 50-30-20 budget breakdown 
            (needs, wants, savings) and target emergency fund size.
            
            REACT CONTROL:
            - If the 'Budget Calculator' tool already returned the required calculation, STOP. 
              Do not call tools with identical inputs again. 
              Immediately compile the output and write the final response.
            """,
            agent=budget_agent,
            expected_output="""A report containing the parsed income, expenses, monthly surplus, 
                               a 50-30-20 budget split recommendation, and 6-month emergency fund target."""
        )

        # 2. Investment Task
        investment_task = Task(
            description=f"""
            Analyze the user's investment options and goals from the query: '{user_query}'
            
            If any SIP, monthly investment, or investment compounding projections are requested or implied, 
            run the 'SIP Calculator' tool with the corresponding monthly investment, expected return rate, and tenure. 
            Formulate recommendations on short-term vs long-term assets (mutual funds, PPF, gold).
            
            REACT CONTROL:
            - If the 'SIP Calculator' tool already returned the required calculation, STOP. 
              Do not call tools with identical inputs again.
              Immediately compile the output and write the final response.
            """,
            agent=investment_agent,
            expected_output="""An investment roadmap detailing suggested SIP targets, asset allocations, 
                               and projected maturity compounding outcomes.""",
            context=[budget_task]
        )

        # 3. Debt Task
        debt_task = Task(
            description=f"""
            Analyze loan liabilities, outstanding debt, or EMI questions from the query: '{user_query}'
            
            If a loan principal, interest rate, and tenure are present or implied, run the 'EMI Calculator' tool 
            to compute the monthly EMI payment, total interest, and payoff schedule. Outline payoff priority 
            using the debt avalanche or debt snowball method.
            
            REACT CONTROL:
            - If the 'EMI Calculator' tool already returned the required calculation, STOP. 
              Do not call tools with identical inputs again.
              Immediately compile the output and write the final response.
            """,
            agent=debt_agent,
            expected_output="""A debt analysis listing calculated loan EMIs, interest payable, 
                               and a prioritized debt payoff strategy.""",
            context=[budget_task]
        )

        # 4. Tax Task
        tax_task = Task(
            description=f"""
            Analyze income tax saving and optimization queries from the query: '{user_query}'
            
            If income is provided or implied, run the 'Tax Calculator' tool to estimate tax liabilities 
            under the Old vs New Regime comparison. Guide on maximizing tax deductions under Section 80C and 80D.
            
            REACT CONTROL:
            - If the 'Tax Calculator' tool already returned the required calculation, STOP. 
              Do not call tools with identical inputs again.
              Immediately compile the output and write the final response.
            """,
            agent=tax_agent,
            expected_output="""A tax advisory detailing the Old vs New Tax Regime calculations, recommended regime 
                               selection, and legal tax deductions under 80C/80D.""",
            context=[budget_task]
        )

        # 5. Financial Planner Compilation Task
        report_task = Task(
            description=f"""
            Generate a comprehensive client-ready financial advisory report.
            Synthesize all computations, allocations, payoff schedules, and tax options compiled by the previous tasks.
            
            Original query context: '{user_query}'
            
            Your final response MUST be a single, valid JSON object matching the following structure.
            Do not include any greetings, conversational pleasantries, extra text, or markdown code blocks (do not wrap in ```json).
            Return ONLY the raw JSON object string:
            
            {{
              "summary": "A high-level synthesis of the user's financial state incorporating the exact calculation outputs.",
              "recommendations": ["Recommendation 1", "Recommendation 2"],
              "risks": ["Risk 1", "Risk 2"],
              "action_plan": ["Step 1", "Step 2"]
            }}
            """,
            agent=financial_planner_agent,
            expected_output="A single structured JSON object with keys: summary, recommendations, risks, action_plan.",
            context=[budget_task, investment_task, debt_task, tax_task]
        )

        # Build sequential Crew
        crew = Crew(
            agents=[budget_agent, investment_agent, debt_agent, tax_agent, financial_planner_agent],
            tasks=[budget_task, investment_task, debt_task, tax_task, report_task],
            process=Process.sequential,
            verbose=True
        )

        logger.info("Executing sequential CrewAI tasks...")
        result = crew.kickoff()
        logger.info("CrewAI execution completed successfully.")
        
        return str(result)
