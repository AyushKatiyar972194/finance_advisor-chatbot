from crewai import LLM

def get_ollama_model():
    return LLM(
        model="ollama/llama2",
        base_url="http://localhost:11434",
        temperature=0.7
    )