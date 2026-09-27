import os
import streamlit as st
from agent import run_agent
from tools import load_plan
from focus_timer import render_focus_timer

st.set_page_config(page_title="AI Study Planner Agent", page_icon="📚")

st.title("📚 AI Study Planner Agent")
st.caption("An agentic AI that plans, prioritizes, and reorganizes your study schedule.")

# placeholder — actual rendering happens after sidebar checkbox is defined below

# ---- Show existing saved plan (if any) so the student sees persistence ----
existing_plan = load_plan()
if existing_plan and existing_plan.get("schedule"):
    with st.expander("📋 Your current saved plan (from last session)", expanded=False):
        st.caption(f"Last updated: {existing_plan.get('last_updated', 'Unknown')}")
        for item in existing_plan["schedule"]:
            st.markdown(f"**{item['subject']}** — {item['hours_allocated']} hrs — *{item.get('topics', 'General revision')}*")

# ---- Session state: keeps chat history and Gemini's conversation history alive across reruns ----
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []
if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = []

# ---- Sidebar: quick example prompts + reset button ----
with st.sidebar:
    st.header("Try an example")
    example_1 = st.button("📌 New study plan (Maths, Physics, C)")
    example_2 = st.button("🔄 I studied less than planned")

    st.divider()
    if st.button("🗑️ Reset plan (clear saved data)"):
        if os.path.exists("study_plan.json"):
            os.remove("study_plan.json")
        st.session_state.display_messages = []
        st.session_state.gemini_history = []
        st.success("Plan and chat cleared!")
        st.rerun()

    st.divider()
    st.markdown(
        "**How this agent works:**\n\n"
        "1. Understands your message\n"
        "2. Decides which tool to use\n"
        "3. Calls the tool (real Python function)\n"
        "4. Returns the result + explains its reasoning"
    )

    st.divider()
    show_timer = st.checkbox("⏱️ Show Focus Timer")

if show_timer:
    st.subheader("⏱️ Focus Mode")
    render_focus_timer()
    st.divider()

# ---- Show past chat messages ----
for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("action_log"):
            with st.expander("🔧 See what the agent did (tool calls)"):
                for action in msg["action_log"]:
                    st.markdown(f"**Tool called:** `{action['tool']}`")
                    st.json(action["args"])
                    st.markdown("**Result:**")
                    st.json(action["result"])
                    st.divider()

# ---- Handle example button clicks ----
user_input = None
if example_1:
    user_input = ("I have Maths on 2026-09-29, Physics on 2026-10-01 and C Programming "
                  "on 2026-10-03. Physics is my weakest subject (high difficulty), Maths "
                  "is medium, C is low difficulty. I've completed 40% of Maths, 20% Physics, "
                  "60% C Programming. I have 3 hours to study today.")
elif example_2:
    user_input = "I only studied 1 hour today instead of the 3 hours I had planned."

# ---- Chat input box ----
typed_input = st.chat_input("Tell me about your subjects, exams, or study progress...")
if typed_input:
    user_input = typed_input

# ---- Process the user's message through the agent ----
if user_input:
    st.session_state.display_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and deciding which tools to use..."):
            try:
                final_text, action_log = run_agent(user_input, st.session_state.gemini_history)
                st.markdown(final_text)

                # ---- Show a bar chart if a schedule was generated/updated ----
                schedule_data = None
                for action in action_log:
                    if action["tool"] in ("generate_schedule", "update_plan") and isinstance(action["result"], list):
                        schedule_data = action["result"]

                if schedule_data:
                    st.markdown("**📊 Time Allocation:**")
                    chart_dict = {item["subject"]: item["hours_allocated"] for item in schedule_data}
                    st.bar_chart(chart_dict)

                if action_log:
                    with st.expander("🔧 See what the agent did (tool calls)"):
                        for action in action_log:
                            st.markdown(f"**Tool called:** `{action['tool']}`")
                            st.json(action["args"])
                            st.markdown("**Result:**")
                            st.json(action["result"])
                            st.divider()

                st.session_state.display_messages.append({
                    "role": "assistant",
                    "content": final_text,
                    "action_log": action_log
                })

            except Exception as e:
                st.error(f"Something went wrong: {e}")