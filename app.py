import streamlit as st
import urllib.request
import json
import uuid

# Page setup
st.set_page_config(
    page_title="💰 Personal Finance Advisor",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Personal Finance Advisor")
st.caption("Powered by FastAPI + CrewAI + LangChain + ChatOllama")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Configuration")
    api_url = st.text_input("Backend API URL", value="http://127.0.0.1:8000")
    
    # Simple connection check indicator
    try:
        req = urllib.request.Request(f"{api_url}/health", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "healthy":
                st.success("🟢 API Status: Connected")
            else:
                st.warning("⚠️ API Status: Unhealthy")
    except Exception:
        st.error("🔴 API Status: Disconnected")

# Generate or store a persistent session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Chat history state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": """👋 Hello! I'm your Personal Finance Advisor.

Tell me about your financial situation and I'll help you with:
- 📊 Budget planning & emergency fund targets
- 💹 Investment asset advice & SIP compounding
- 🏦 Tax regime comparisons & Section 80C/80D optimizations
- 💳 Loan EMI calculations & debt management payoff priorities

**Example:** *"I earn ₹50,000/month, spend ₹35,000. How should I plan my finances?"*"""
    })

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input handler
if prompt := st.chat_input("Describe your financial situation..."):
    
    # Render user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Retrieve AI response from the FastAPI POST /chat gateway
    with st.chat_message("assistant"):
        with st.spinner("🤔 Running multi-agent financial planning crew..."):
            try:
                payload = {
                    "session_id": st.session_state.session_id,
                    "message": prompt
                }
                data = json.dumps(payload).encode("utf-8")
                
                req = urllib.request.Request(
                    f"{api_url}/chat",
                    data=data,
                    headers={"Content-Type": "application/json"}
                )
                
                # Execute HTTP Request (with a high timeout of 10 minutes to allow CrewAI runs)
                with urllib.request.urlopen(req, timeout=600) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    ai_response = res_data.get("response", "No response received.")
                
                # Try parsing as JSON to display clean sections
                try:
                    # Clean markdown wrappers if model outputted them anyway
                    cleaned = ai_response.strip()
                    if cleaned.startswith("```json"):
                        cleaned = cleaned[7:]
                    elif cleaned.startswith("```"):
                        cleaned = cleaned[3:]
                    if cleaned.endswith("```"):
                        cleaned = cleaned[:-3]
                    cleaned = cleaned.strip()
                    
                    report = json.loads(cleaned)
                    
                    # Display structured output
                    formatted_text = ""
                    if "summary" in report:
                        st.subheader("📊 Summary")
                        st.write(report["summary"])
                        formatted_text += f"### 📊 Summary\n{report['summary']}\n\n"
                    
                    if "recommendations" in report and report["recommendations"]:
                        st.subheader("💡 Recommendations")
                        for rec in report["recommendations"]:
                            st.write(f"- {rec}")
                        formatted_text += "### 💡 Recommendations\n" + "\n".join([f"- {r}" for r in report["recommendations"]]) + "\n\n"
                        
                    if "risks" in report and report["risks"]:
                        st.subheader("⚠️ Risks")
                        for risk in report["risks"]:
                            st.write(f"- {risk}")
                        formatted_text += "### ⚠️ Risks\n" + "\n".join([f"- {r}" for r in report["risks"]]) + "\n\n"
                        
                    if "action_plan" in report and report["action_plan"]:
                        st.subheader("📅 Action Plan")
                        for idx, step in enumerate(report["action_plan"], 1):
                            st.write(f"{idx}. {step}")
                        formatted_text += "### 📅 Action Plan\n" + "\n".join([f"{i}. {s}" for i, s in enumerate(report["action_plan"], 1)]) + "\n\n"
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": formatted_text
                    })
                except Exception:
                    # Fallback to direct raw output if it is not valid JSON
                    st.markdown(ai_response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_response
                    })
                
            except Exception as e:
                error_msg = (
                    f"❌ Connection Error: {str(e)}\n\n"
                    f"Please verify that the FastAPI backend server is running at **{api_url}**."
                )
                st.error(error_msg)