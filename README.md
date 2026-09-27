<HEAD
# 📚 AI Study Planner Agent

An **agentic AI system** that helps students plan, prioritize, and reorganize their study schedules — built for [Course/Assignment Name].

Unlike a simple chatbot, this agent **reasons about the student's situation and takes real actions** using tools: it calculates subject priorities, generates a study schedule, saves it, and reorganizes it when the student's situation changes.

## 🎯 Problem It Solves

Students juggling multiple subjects, exams, and varying difficulty levels often struggle to allocate study time effectively — especially when plans get disrupted (e.g., studying less than intended on a given day). This agent automates that reasoning and planning process.

## 🧠 How It Works (Agent Architecture)

This is an **agent**, not a chatbot, because it doesn't just respond with text — it decides which tool to use, executes real Python functions, and acts on their results.

**Flow:**

1. **Understand** — The student describes their subjects, exam dates, available time, weak areas, or a change in situation (e.g., "I studied less than planned").
2. **Reason & Decide** — Gemini (the LLM) analyzes the request and decides which tool(s) are needed, in what order.
3. **Act (Tool Use)** — The agent calls real Python functions:
   - `calculate_priority()` — scores each subject by urgency (exam proximity), difficulty, and progress
   - `generate_schedule()` — distributes available hours across subjects based on priority
   - `save_plan()` — persists the plan to `study_plan.json`
   - `update_plan()` — reorganizes the **remaining** plan when the student's situation changes
4. **Return Result** — The agent explains its reasoning in plain language and shows the student their updated plan.

This loop (reason → act → observe result → reason again) repeats until the agent has a complete answer — this is what makes it agentic.

## 🛠️ Tech Stack

- **Python** — core logic
- **Gemini API** (`google-genai` SDK, model: `gemini-3.8-flash`) — reasoning + function calling
- **Streamlit** — web interface
- **GitHub** — version control
- **Streamlit Community Cloud** — deployment

## 📂 Project Structure

# Study_planner
03b4497591473f8b26cfc97e92a40ce5353a4c80
