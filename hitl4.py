from dotenv import load_dotenv
from typing import Annotated, List

from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import HumanInTheLoopMiddleware

from pydantic import BaseModel

load_dotenv()

searchTool = DuckDuckGoSearchResults()

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.7)


class State(BaseModel):
    messages: Annotated[List[BaseMessage], add_messages]


@tool
def SearchResultFromInternet(query: str):
    """Searches internet queries and real time updates"""

    decision = interrupt("Do you want to search the internet? (yes/no)")

    if str(decision).lower() not in ["yes", "y"]:
        return "Internet search cancelled"

    return searchTool.invoke(query)


@tool
def MathQuestionsResolve(query: str):
    """Solves Maths problems only"""

    decision = interrupt("Do you want to solve this math question? (yes/no)")

    if str(decision).lower() not in ["yes", "y"]:
        return "Math solving cancelled"

    return llm.invoke(query).content


tools = [SearchResultFromInternet, MathQuestionsResolve]

hitl = HumanInTheLoopMiddleware(interrupt_on={"MathQuestionsResolve": True, "SearchResultFromInternet": True})
tool_node = ToolNode(tools)

llm_with_tools = llm.bind_tools(tools)

checkpointer = InMemorySaver()


def AskChatbot(state: State):
    response = llm_with_tools.invoke(state.messages)
    
    print("\nTool Calls:", response.tool_calls)

    return {"messages": [response]}


graph = StateGraph(State)

graph.add_node("Ask_Questions", AskChatbot)
graph.add_node("tools", tool_node)

graph.add_edge(START, "Ask_Questions")

graph.add_conditional_edges("Ask_Questions", tools_condition)

graph.add_edge("tools", "Ask_Questions")

workflow = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}

user_input = input("What is your query? ")

result = workflow.invoke(
    {"messages": [{"role": "user", "content": user_input}]}, config=config
)

interrupts = result.get("__interrupt__", [])

if interrupts:

    print("\nInterrupt:")
    print(interrupts[0].value)

    decision = input("\nEnter yes/no: ")

    result = workflow.invoke(Command(resume=decision), config=config)

print("\nFinal Messages:\n")

for msg in result["messages"]:
    print(msg)
