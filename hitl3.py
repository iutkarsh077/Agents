from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Annotated
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import InMemorySaver
import os

load_dotenv()


class ConversationState(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages]


llm = ChatOpenAI(temperature=0.7, model="gpt-5.4-mini")


@tool
def DeleteFile(filePath: str) -> str:
    """Deletes a file from the system."""

    decision = interrupt(f"Do you want to delete '{filePath}' ? (yes/no): ")
    if str(decision).lower() not in ["yes", "y"]:
        return f"Deletion of '{filePath}' was cancelled."
    try:
        os.remove(filePath)
        return f"File '{filePath}' has been deleted successfully."
    except FileNotFoundError:
        return f"File '{filePath}' not found."
    except Exception as e:
        return f"An error occurred while trying to delete the file: {str(e)}"


@tool
def ReadFile(filePath: str) -> str:
    """Reads the content of a file."""

    decision = interrupt(f"Do you want to read '{filePath}' ? (yes/no): ")

    if str(decision).lower() not in ["yes", "y"]:
        return f"Reading of '{filePath}' was cancelled."
    try:
        with open(filePath, "r") as file:
            content = file.read()
            print(f"Content of '{filePath}':\n{content}\n")
        return content
    except FileNotFoundError:
        return f"File '{filePath}' not found."
    except Exception as e:
        return f"An error occurred while trying to read the file: {str(e)}"


hitl = HumanInTheLoopMiddleware(interrupt_on={"DeleteFile": True, "ReadFile": True})

tools = [DeleteFile, ReadFile]
checkpointer = InMemorySaver()
tool_Node = ToolNode(tools)
llm_with_tools = llm.bind_tools(tools)


graph = StateGraph(ConversationState)


def Ask_Questions(state: ConversationState) -> ConversationState:
    """Asks questions to the user."""
    last_message = state.messages[-1].content
    response = llm_with_tools.invoke(last_message)
    return {"messages": [response]}


graph.add_node("Ask_Questions", Ask_Questions)
graph.add_node("tools", tool_Node)


graph.add_edge(START, "Ask_Questions")

graph.add_conditional_edges("Ask_Questions", tools_condition)

graph.add_edge("tools", "Ask_Questions")


workflow = graph.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "1"}}
user_input = input("Enter a command (e.g., 'Delete temp.txt' or 'Read temp.txt'): ")
result = workflow.invoke({"messages": [{"role": "user", "content": user_input}]}, config=config)

interrupts = result.get("__interrupt__", [])

print("result is:", result, "\n\n")

if interrupt:
    print("Agent requested human intervention for tool execution.\n")
    print(interrupts[0].value, "\n")
    decision = input(
        "Agent requested human intervention for tool execution. Please provide the necessary input yes/no: "
    )

    result = workflow.invoke(Command(resume=decision), config=config)


for message in result["messages"]:
    print("\n", message)
