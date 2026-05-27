from crewai import LLM
import os
from dotenv import load_dotenv

load_dotenv()

def generate_finance_code(task_description: str) -> str:
    """
    Uses Gemini to generate Python code
    for financial calculations
    """
    llm = LLM(
        model="gemini/gemini-flash-lite-latest",
        api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0
    )
    
    prompt = (
        "You are a financial Python programmer. Write clean, simple Python code for financial calculations. "
        "Only return the raw python code without any markdown formatting or explanation.\n\n"
        f"Write Python code for: {task_description}"
    )
    
    # call() returns the response string directly
    response = llm.call(messages=[{"role": "user", "content": prompt}])
    
    # Clean up markdown code blocks if the LLM includes them
    code = response.strip()
    if code.startswith("```python"):
        code = code[9:]
    elif code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
        
    return code.strip()

def run_finance_calculation(description: str):
    """Generate and execute financial calculation code"""
    code = generate_finance_code(description)
    
    print("\n📝 Generated Code:\n", code)
    
    # Execute the generated code safely
    local_vars = {}
    try:
        exec(code, {}, local_vars)
        if local_vars:
            # Return the last assigned variable's value
            return list(local_vars.values())[-1], code
        return "Executed successfully, but no result produced.", code
    except Exception as e:
        return f"Error running code: {e}", code