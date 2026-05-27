import streamlit as st
from crew import run_finance_crew
from tools.codex_tool import run_finance_calculation
import time

# Page setup
st.set_page_config(
    page_title="💰 Personal Finance Advisor",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Personal Finance Advisor")
st.caption("Powered by Gemini + CrewAI + LangChain + Ollama + Codex")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    use_ollama = st.toggle(
        "Use Offline Mode (Ollama)",
        value=False,
        help="Switch to local AI — no internet needed"
    )
    
    if use_ollama:
        st.success("🔒 Using Ollama (Offline)")
    else:
        st.info("🌐 Using Gemini (Online)")
    
    st.divider()
    
    st.header("🧮 Quick Calculator")
    calc_type = st.selectbox("Calculate", ["EMI", "SIP Returns"])
    
    if calc_type == "EMI":
        principal = st.number_input("Loan Amount (₹)", value=500000)
        rate = st.number_input("Interest Rate (%)", value=8.5)
        years = st.number_input("Years", value=5)
        
        if st.button("Calculate EMI"):
            result = run_finance_calculation(
                f"Calculate EMI for loan of ₹{principal} at {rate}% for {years} years"
            )
            st.success(result[0] if isinstance(result, tuple) else result)
    
    elif calc_type == "SIP Returns":
        monthly = st.number_input("Monthly SIP (₹)", value=5000)
        rate = st.number_input("Expected Return (%)", value=12.0)
        years = st.number_input("Investment Years", value=10)
        
        if st.button("Calculate Returns"):
            result = run_finance_calculation(
                f"Calculate SIP returns for ₹{monthly}/month at {rate}% for {years} years"
            )
            st.success(result[0] if isinstance(result, tuple) else result)

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": """👋 Hello! I'm your Personal Finance Advisor.

Tell me about your financial situation and I'll help you with:
- 📊 Budget planning
- 💹 Investment advice  
- 🏦 Tax saving strategies
- 💳 Debt management

**Example:** *"I earn ₹50,000/month, spend ₹35,000, have a home loan of ₹20 lakh. How should I plan my finances?"*"""
    })

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Describe your financial situation..."):
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Analyzing your finances..."):
            try:
                response = run_finance_crew(
                    prompt,
                    use_ollama=use_ollama
                )
                st.markdown(response)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}\n\nMake sure your API keys are set correctly in .env file"
                st.error(error_msg)
                