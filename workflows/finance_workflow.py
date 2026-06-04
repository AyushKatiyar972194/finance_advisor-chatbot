import logging
import urllib.request
import json
from crewai import Crew, Task, Process
from config.settings import settings
from agents.budget_agent import get_budget_agent
from agents.investment_agent import get_investment_agent
from agents.debt_agent import get_debt_agent
from agents.tax_agent import get_tax_agent
from agents.financial_planner_agent import get_financial_planner_agent
from tools.calculator_tool import budget_calculator, sip_calculator, emi_calculator, tax_calculator

logger = logging.getLogger(__name__)

class FinanceWorkflow:
    def __init__(self):
        pass

    def _extract_parameters(self, user_query: str) -> dict:
        """
        Extract financial parameters from query using a structured JSON Ollama call.
        """
        system_prompt = (
            "You are an information extraction assistant. Extract financial details from the user's query into a JSON object.\n"
            "If a value is not mentioned, use null. Use the following keys:\n"
            "- monthly_income (number, total monthly earnings)\n"
            "- monthly_expenses (number, total monthly expenses)\n"
            "- sip_monthly_investment (number, if they specify a specific SIP amount to invest)\n"
            "- sip_expected_return_rate (number, default to 12.0 if not specified but SIP is mentioned)\n"
            "- sip_years (number, default to 5 if not specified but SIP is mentioned)\n"
            "- loan_principal (number, total loan amount)\n"
            "- loan_interest_rate (number, annual interest rate percentage)\n"
            "- loan_years (number, loan duration/tenure in years)\n"
            "- annual_taxable_income (number, total taxable income per year)\n"
            "Return ONLY a raw JSON object. Do not wrap in markdown blocks."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Query: {user_query}"}
        ]

        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "format": "json"
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=300) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                content = res_data["message"]["content"].strip()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Error extracting parameters: {e}")
            return {}

    def run(self, user_query: str) -> str:
        logger.info(f"Initiating Finance Workflow Crew with user query: {user_query}")
        
        # Instantiate agents locally for thread-safety
        budget_agent = get_budget_agent()
        investment_agent = get_investment_agent()
        debt_agent = get_debt_agent()
        tax_agent = get_tax_agent()
        financial_planner_agent = get_financial_planner_agent()
        
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

        # 0. Upfront parameter extraction
        params = self._extract_parameters(user_query)
        logger.info(f"Extracted params: {params}")

        # Regex fallback if parameter extraction timed out or returned empty
        if not params:
            import re
            logger.info("Ollama parameter extraction failed or timed out. Running Python regex fallback extraction...")
            # Normalize query: replace common markers
            norm_query = user_query.replace(",", "")
            # Find all numbers
            numbers = [float(x) for x in re.findall(r'\b\d+(?:\.\d+)?\b', norm_query)]
            # If we find numbers, assign larger to income and smaller to expenses
            if len(numbers) >= 2:
                params["monthly_income"] = max(numbers)
                params["monthly_expenses"] = min(numbers)
                logger.info(f"Regex extracted monthly_income={params['monthly_income']}, monthly_expenses={params['monthly_expenses']}")
            elif len(numbers) == 1:
                params["monthly_income"] = numbers[0]
                logger.info(f"Regex extracted monthly_income={params['monthly_income']}")

        # Extract parameters with safe conversions
        def safe_float(val):
            try:
                return float(val) if val is not None else None
            except:
                return None

        def safe_int(val):
            try:
                return int(val) if val is not None else None
            except:
                return None

        monthly_income = safe_float(params.get("monthly_income"))
        monthly_expenses = safe_float(params.get("monthly_expenses"))
        sip_monthly = safe_float(params.get("sip_monthly_investment"))
        sip_rate = safe_float(params.get("sip_expected_return_rate"))
        sip_years = safe_int(params.get("sip_years"))
        loan_principal = safe_float(params.get("loan_principal"))
        loan_interest_rate = safe_float(params.get("loan_interest_rate"))
        loan_years = safe_int(params.get("loan_years"))
        annual_taxable_income = safe_float(params.get("annual_taxable_income"))

        # Smart defaults
        if monthly_income is not None:
            if annual_taxable_income is None:
                annual_taxable_income = monthly_income * 12.0

        if monthly_income is not None and monthly_expenses is not None:
            surplus = monthly_income - monthly_expenses
            if sip_monthly is None and surplus > 0:
                sip_monthly = surplus

        # Run calculators in python
        # 1. Budget calculation
        if monthly_income is not None and monthly_expenses is not None:
            budget_result = budget_calculator.invoke({
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses
            })
        else:
            budget_result = "No monthly income or expenses specified in the query. Budget calculations skipped."

        # 2. SIP calculation
        if sip_monthly is not None:
            sip_result = sip_calculator.invoke({
                "monthly_investment": sip_monthly,
                "expected_return_rate": sip_rate if sip_rate is not None else 12.0,
                "years": sip_years if sip_years is not None else 5
            })
        else:
            sip_result = "No investment or SIP details specified. SIP calculations skipped."

        # 3. Debt calculation
        if loan_principal is not None:
            debt_result = emi_calculator.invoke({
                "principal": loan_principal,
                "annual_interest_rate": loan_interest_rate if loan_interest_rate is not None else 8.5,
                "years": loan_years if loan_years is not None else 5
            })
        else:
            debt_result = "No loan or EMI details specified. Debt payoff calculations skipped."

        # 4. Tax calculation
        if annual_taxable_income is not None:
            tax_result = tax_calculator.invoke({
                "annual_income": annual_taxable_income
            })
        else:
            tax_result = "No income details specified. Tax calculations skipped."

        # Build tasks dynamically based on what was provided/extracted
        active_agents = []
        active_tasks = []

        # 1. Budget Task
        budget_task = Task(
            description=f"""
            Evaluate these calculated budget results:
            {budget_result}
            
            Confirm if the current savings rate is healthy (e.g. check if it is below 20%).
            Formulate emergency preparedness recommendations based on the 6-month target emergency fund.
            """,
            agent=budget_agent,
            expected_output="""A report containing the parsed income, expenses, monthly surplus, 
                               a 50-30-20 budget split recommendation, and 6-month emergency fund target."""
        )

        if monthly_income is not None and monthly_expenses is not None:
            active_agents.append(budget_agent)
            active_tasks.append(budget_task)

        # Context lists
        budget_context = [budget_task] if (budget_task in active_tasks) else []

        # 2. Investment Task
        investment_task = Task(
            description=f"""
            Evaluate these calculated investment compounding results:
            {sip_result}
            
            Based on the client's monthly surplus and investment goals, suggest long-term vs short-term 
            asset allocations (mutual funds, PPF, gold).
            """,
            agent=investment_agent,
            expected_output="""An investment roadmap detailing suggested SIP targets, asset allocations, 
                               and projected maturity compounding outcomes.""",
            context=budget_context
        )

        if sip_monthly is not None:
            active_agents.append(investment_agent)
            active_tasks.append(investment_task)

        # 3. Debt Task
        debt_task = Task(
            description=f"""
            Evaluate these calculated loan EMI and payoff results:
            {debt_result}
            
            Outline a prioritized debt payoff strategy using the debt avalanche or debt snowball method.
            """,
            agent=debt_agent,
            expected_output="""A debt analysis listing calculated loan EMIs, interest payable, 
                               and a prioritized debt payoff strategy.""",
            context=budget_context
        )

        if loan_principal is not None:
            active_agents.append(debt_agent)
            active_tasks.append(debt_task)

        # 4. Tax Task
        tax_task = Task(
            description=f"""
            Evaluate these calculated Old vs New tax regime results:
            {tax_result}
            
            Compare tax efficiency, recommend the optimal tax regime, and identify legal tax deductions (Section 80C/80D).
            """,
            agent=tax_agent,
            expected_output="""A tax advisory detailing the Old vs New Tax Regime calculations, recommended regime 
                               selection, and legal tax deductions under 80C/80D.""",
            context=budget_context
        )

        if annual_taxable_income is not None:
            active_agents.append(tax_agent)
            active_tasks.append(tax_task)

        # Fallback if no task is active, add budget task
        if not active_tasks:
            active_agents.append(budget_agent)
            active_tasks.append(budget_task)

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
            context=active_tasks.copy()
        )

        active_agents.append(financial_planner_agent)
        active_tasks.append(report_task)

        # Build sequential Crew
        crew = Crew(
            agents=active_agents,
            tasks=active_tasks,
            process=Process.sequential,
            verbose=True
        )

        logger.info("Executing sequential CrewAI tasks...")
        result = crew.kickoff()
        logger.info("CrewAI execution completed successfully.")
        
        return str(result)
