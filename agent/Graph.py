from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from prompt import *
from states import *
from tools import write_file, read_file, get_current_directory, list_files
from reviewer import reviewer_agent
from langgraph.constants import END
from langgraph.graph import StateGraph

llm = ChatGroq(model="openai/gpt-oss-120b")
from pydantic import BaseModel ,Field

user_prompt = "create a simple calculator web application"

def planner_agent(state:dict) ->dict:
    user_prompt=state["user_prompt"]
    resp = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))
    if resp is None:
        raise ValueError("Planner did not return a valid response.")

    return{ "plan": resp}

def architect_agent(state: dict) -> dict:
    """Creates TaskPlan from Plan."""
    plan: Plan = state["plan"]
    resp = llm.with_structured_output(TaskPlan).invoke(
        architect_prompt(plan=plan.model_dump_json())
    )
    if resp is None:
        raise ValueError("Planner did not return a valid response.")

    resp.plan = plan
    print(resp.model_dump_json())
    return {"task_plan": resp}

def coder_agent(state: dict) -> dict:
    coder_state= state.get("coder_state")
    if coder_state is None:
         coder_state= CoderState(task_plan=state["task_plan"],current_step_idx=0)

    steps = coder_state.task_plan.implementation_steps
    if coder_state.current_step_idx >= len(steps):
          return{"coder_state": coder_state,"status":"DONE"}

    current_task = steps[coder_state.current_step_idx]

    existing_content= read_file.run(current_task.filepath)
    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use write_file(path, content) to save your changes."
      )
    system_prompt = coder_system_prompt()

    coder_tools = [read_file, write_file, list_files, get_current_directory]
    react_agent = create_react_agent(llm, coder_tools)
    react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},
                                     {"role": "user", "content": user_prompt}]})

    coder_state.current_step_idx += 1

    return {"coder_state": coder_state }








graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", coder_agent)
graph.add_node("reviewer", reviewer_agent)

graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")
graph.add_conditional_edges(
    "coder",
    lambda s: "reviewer" if s.get("status") == "DONE" else "coder",
    {"reviewer": "reviewer", "coder": "coder"}
)
graph.add_edge("reviewer", END)

graph.set_entry_point("planner")


agent = graph.compile()

user_prompt = "Create a simple Flappy Bird style browser game using HTML, CSS, and JavaScript with canvas. The bird falls due to gravity and flaps upward on click or spacebar. Pipes scroll from right to left with gaps to fly through. Track and display the score, and show a game over screen with a restart button on collision."

result = agent.invoke({"user_prompt":user_prompt}, {"recursion_limit": 100})
print(result)