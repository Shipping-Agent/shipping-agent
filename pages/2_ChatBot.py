import streamlit as st
from services.aws_agent_connector import AWSAgentConnector
from datetime import datetime
import time

# Load CSS
with open("styles/chat_ui.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# === NAVBAR ===
st.markdown("""
<div class="navbar">
    <h2>📦 Shipping Assistant</h2>
    <div class="nav-links">
        <a href="/Home" target="_self">Home</a>
        <a href="/Chatbot" target="_self">Chatbot</a>
        <a href="https://aws.amazon.com/bedrock/" target="_blank">AWS Bedrock</a>
        <a href="mailto:support@example.com">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent_connector' not in st.session_state:
    st.session_state.agent_connector = AWSAgentConnector()
    success, message = st.session_state.agent_connector.initialize_connection()
    st.session_state.connected = success
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session-{int(time.time())}"
if 'connected' not in st.session_state:
    st.session_state.connected = False

st.header("💬 Chat with Your Agent")

# Status box
st.markdown(f"""
<div class="status-box {'status-connected' if st.session_state.connected else 'status-disconnected'}">
    {'✅ <strong>Connected</strong>' if st.session_state.connected else '❌ <strong>Not Connected</strong>'} 
</div>
""", unsafe_allow_html=True)

# Chat history
for message in st.session_state.messages:
    msg_type = "user-message" if message["role"] == "user" else "agent-message"
    label = "You" if message["role"] == "user" else "Agent"
    st.markdown(f"""
    <div class="{msg_type}">
        <strong>{label}:</strong> {message["content"]}
        <small style="float: right; color: #666;">{message["timestamp"]}</small>
    </div>
    """, unsafe_allow_html=True)

# Chat input
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    user_input = col1.text_input("Ask...", label_visibility="collapsed")
    send_button = col2.form_submit_button("Send 📤")

    if send_button and user_input:
        if not st.session_state.connected:
            st.error("Please connect first.")
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": timestamp})
            with st.spinner("Agent is thinking..."):
                response = st.session_state.agent_connector.send_message(user_input, st.session_state.session_id)
            st.session_state.messages.append({"role": "agent", "content": response, "timestamp": datetime.now().strftime("%H:%M:%S")})
            st.rerun()

# Quick actions
st.markdown("### 🚀 Quick Actions")
col1, col2, col3 = st.columns(3)
def quick_action(prompt):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": timestamp})
    with st.spinner("Agent is responding..."):
        response = st.session_state.agent_connector.send_message(prompt, st.session_state.session_id)
    st.session_state.messages.append({"role": "agent", "content": response, "timestamp": datetime.now().strftime("%H:%M:%S")})
    st.rerun()

with col1:
    if st.button("📋 Get Shipping Rates", use_container_width=True) and st.session_state.connected:
        quick_action("Can you help me get shipping rates for a package?")
with col2:
    if st.button("📦 Track Package", use_container_width=True) and st.session_state.connected:
        quick_action("I need help tracking a package. What information do you need?")
with col3:
    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = f"session-{int(time.time())}"
        st.rerun()