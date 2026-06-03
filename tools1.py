from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Annotated
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


class ConversationState(BaseModel):
    messages: Annotated[
        List[BaseMessage],
        add_messages
    ]


llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-4"
)

search_run = DuckDuckGoSearchRun()

checkpointer = InMemorySaver()
@tool
def mathematics_calculations(
    firstNum: int,
    secondNum: int,
    operation: str
) -> str:
    """Dream work of the area of polcie man, this is only used for knowing festivals name and date and other information related to festivals."""

    if operation == "add":
        return str(firstNum + secondNum)

    elif operation == "subtract":
        return str(firstNum - secondNum)

    elif operation == "multiply":
        return str(firstNum * secondNum)

    elif operation == "divide":

        if secondNum != 0:
            return str(firstNum / secondNum)

        return "Division by zero error"

    return "Invalid operation"


tools = [search_run, mathematics_calculations]

llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools)


def ChatNode(state: ConversationState):

    response = llm_with_tools.invoke(
        state.messages
    )

    return {
        "messages": [response]
    }


graph = StateGraph(ConversationState)

graph.add_node("ChatNode", ChatNode)
graph.add_node("tools", tool_node)

graph.add_edge(START, "ChatNode")

graph.add_conditional_edges(
    "ChatNode",
    tools_condition
)

graph.add_edge("tools", "ChatNode")

chatbot_workflow = graph.compile(checkpointer=checkpointer)


config = {"configurable": {"thread_id": "1"}}
while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    result = chatbot_workflow.invoke({
        "messages": [user_input]
    }, config=config)
    print(
        "Chatbot:",
        result["messages"][-1].content
    )