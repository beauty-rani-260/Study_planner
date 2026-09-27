import os
import json
import time
from datetime import date
from google import genai
from google.genai import types
from dotenv import load_dotenv

from tools import calculate_priority, generate_schedule, save_plan, update_plan, load_plan

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-flash-lite-latest"

# ----- Tool declarations: this tells Gemini what tools exist and when to use them -----

tools_config = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="calculate_priority",
            description="Calculates priority scores for a list of subjects based on exam date, difficulty and progress. Use this first whenever the student gives new subject/exam info.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "subjects": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "name": {"type": "STRING"},
                                "exam_date": {"type": "STRING", "description": "Format YYYY-MM-DD"},
                                "difficulty": {"type": "STRING", "enum": ["low", "medium", "high"]},
                                "progress": {"type": "NUMBER", "description": "Percent already studied, 0-100"},
                                "topics": {"type": "STRING"}
                            },
                            "required": ["name", "exam_date"]
                        }
                    }
                },
                "required": ["subjects"]
            }
        ),
        types.FunctionDeclaration(
            name="generate_schedule",
            description="Creates a study schedule by distributing available hours across prioritized subjects. Call this after calculate_priority.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "available_hours": {"type": "NUMBER", "description": "Hours the student has available today"}
                },
                "required": ["available_hours"]
            }
        ),
        types.FunctionDeclaration(
            name="save_plan",
            description="Saves the generated study plan permanently so it can be reloaded later.",
            parameters={"type": "OBJECT", "properties": {}}
        ),
        types.FunctionDeclaration(
            name="update_plan",
            description="Use this ONLY when the student says they studied more/less than planned, or their situation changed, and the existing plan needs to be reorganized.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "actual_hours_studied": {"type": "NUMBER"},
                    "planned_hours": {"type": "NUMBER"}
                },
                "required": ["actual_hours_studied", "planned_hours"]
            }
        ),
    ])
]

SYSTEM_INSTRUCTION = (
    "You are a Study Planner Agent. You do not just chat — you take real actions "
    "using tools to help students plan their study time. "
    "Steps to follow: "
    "1) When the student gives subjects/exams/difficulty/progress, call calculate_priority. "
    "2) Then call generate_schedule with their available hours. "
    "3) Then call save_plan to store it. "
    "4) If the student says they studied more/less than planned, call update_plan instead. "
    f"Today's date is {date.today().isoformat()}. "
    "Always explain your reasoning briefly in plain language before/after tool calls, "
    "so the student understands why you prioritized things a certain way."
)


def run_agent(user_message, chat_history=None):
    """
    The agent loop:
    1. Send the user's message to Gemini, along with our tool definitions.
    2. If Gemini decides to call a tool, we run that real Python function.
    3. We send the tool's result BACK to Gemini.
    4. Gemini uses that result to decide the next step (another tool, or final reply).
    5. Repeat until Gemini gives a final text answer.
    """
    contents = list(chat_history) if chat_history else []
    contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

    action_log = []
    _last_subjects = []
    _last_schedule = []

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=tools_config,
    )

    for _ in range(6):  # safety limit on tool-call loops
        response = None
        last_error = None
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=contents,
                    config=config,
                )
                break
            except Exception as e:
                last_error = e
                time.sleep(3)
        if response is None:
            raise last_error

        candidate = response.candidates[0]
        contents.append(candidate.content)

        function_call = None
        for part in candidate.content.parts:
            if part.function_call:
                function_call = part.function_call
                break

        if not function_call:
            final_text = response.text if hasattr(response, "text") else "Done."
            return final_text, action_log

        tool_name = function_call.name
        tool_args = dict(function_call.args)

        if tool_name == "calculate_priority":
            result = calculate_priority(tool_args["subjects"])
            _last_subjects = tool_args["subjects"]
        elif tool_name == "generate_schedule":
            prioritized = calculate_priority(_last_subjects) if _last_subjects else []
            result = generate_schedule(prioritized, tool_args.get("available_hours"))
            _last_schedule = result
        elif tool_name == "save_plan":
            result = save_plan(_last_schedule, _last_subjects)
        elif tool_name == "update_plan":
            result = update_plan(tool_args["actual_hours_studied"], tool_args["planned_hours"])
        else:
            result = {"error": f"Unknown tool {tool_name}"}

        action_log.append({"tool": tool_name, "args": tool_args, "result": result})

        contents.append(types.Content(
            role="user",
            parts=[types.Part(function_response=types.FunctionResponse(
                name=tool_name,
                response={"result": json.dumps(result, default=str)}
            ))]
        ))

    return "Reached max reasoning steps.", action_log