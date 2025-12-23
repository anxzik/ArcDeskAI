import streamlit as st
import requests
import pandas as pd
import time
import os

# Configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://{API_HOST}:{API_PORT}"

st.set_page_config(
    page_title="AgentDesk Console",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 AgentDesk Command Console")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Agents", "Tasks", "Settings"])

def check_api():
    try:
        response = requests.get(f"{API_URL}/", timeout=1)
        return response.status_code == 200, response.json() if response.status_code == 200 else {}
    except:
        return False, {}

api_status, api_info = check_api()

if not api_status:
    st.error(f"❌ API is offline. Is the backend running at {API_URL}?")
    st.info("Run `uvicorn src.api.main:app --reload` in the agentdesk directory.")
else:
    st.sidebar.success(f"✅ API Online ({api_info.get('provider', 'unknown')})")

if page == "Dashboard":
    st.header("Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("System Status")
        if api_status:
            st.write(f"**Provider:** {api_info.get('provider')}")
            st.write("**Active Agents:** (Loading...)")
            # Fetch counts
            try:
                agents = requests.get(f"{API_URL}/agents").json()
                tasks = requests.get(f"{API_URL}/tasks").json()
                st.metric("Agents Online", len(agents))
                st.metric("Total Tasks", len(tasks))
            except:
                st.write("Error fetching metrics")
        else:
            st.write("System Offline")
            
    with col2:
        st.subheader("Recent Activity")
        st.write("No recent logs.")

elif page == "Agents":
    st.header("Active Agents")
    if st.button("Refresh Agents"):
        st.rerun()
        
    try:
        agents = requests.get(f"{API_URL}/agents").json()
        
        for agent in agents:
            with st.container():
                st.markdown(f"### {agent['title']}")
                c1, c2, c3 = st.columns([1, 2, 1])
                c1.write(f"**Role:** {agent['role']}")
                c1.write(f"**Status:** `{agent['status']}`")
                c2.write(f"**Capabilities:** {', '.join(agent['capabilities'])}")
                c3.write(f"**Model:** {agent['llm_config']['model']}")
                st.divider()
    except Exception as e:
        st.error(f"Error fetching agents: {e}")

elif page == "Tasks":
    st.header("Task Management")
    
    tab1, tab2 = st.tabs(["Create Task", "View Tasks"])
    
    with tab1:
        with st.form("new_task_form"):
            title = st.text_input("Task Title")
            desc = st.text_area("Description")
            priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            submitted = st.form_submit_button("Launch Task")
            
            if submitted:
                if not title:
                    st.warning("Title required")
                else:
                    try:
                        res = requests.post(f"{API_URL}/tasks", json={
                            "title": title,
                            "description": desc,
                            "priority": priority
                        })
                        if res.status_code == 200:
                            st.success(f"Task created: {res.json()['task_id']}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Error: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tab2:
        if st.button("Refresh Tasks"):
            st.rerun()
            
        try:
            tasks = requests.get(f"{API_URL}/tasks").json()
            if tasks:
                df = pd.DataFrame(tasks)
                st.dataframe(
                    df[["task_id", "title", "status", "priority", "assigned_to", "created_at"]],
                    use_container_width=True
                )
            else:
                st.info("No tasks found.")
        except Exception as e:
            st.error(f"Error fetching tasks: {e}")

elif page == "Settings":
    st.header("Configuration")
    st.write("Settings are managed via .env file and environment variables.")
    st.code(f"""
API_URL = {API_URL}
DEFAULT_PROVIDER = {os.getenv('DEFAULT_LLM_PROVIDER', 'unknown')}
    """)
