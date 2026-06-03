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
    messages: Annotated[List[BaseMessage], add_messages]


llm = ChatOpenAI(temperature=0.7, model="gpt-5.4-mini")

search_run = DuckDuckGoSearchRun()


@tool
def ResearchTopics(ConversationState: ConversationState) -> str:
    """Researches topics using DuckDuckGoSearchRun tool."""
    last_message = ConversationState.messages[-1].content
    search_result = llm.invoke(last_message)
    return {
        "messages": [search_result]
    }


@tool
def SummaryOnResearchTopics(ConversationState: ConversationState) -> str:
    """Summarizes the research topics."""
    last_message = ConversationState.messages[-1].content
    summary_result = llm.invoke(last_message)
    return {
        "messages": [summary_result]
    }

tools = [search_run, ResearchTopics, SummaryOnResearchTopics]
llm_with_tools = llm.bind_tools(tools)


def Ask_Questions(state: ConversationState) -> ConversationState:
    """Asks questions to the user."""
    last_message = state.messages[-1].content
    response = llm_with_tools.invoke(last_message)
    return {
        "messages": [response]
    }


tool_node = ToolNode(tools)

graph = StateGraph(ConversationState)
graph.add_node("ChatNode", Ask_Questions)
graph.add_node("tools", tool_node)

graph.add_edge(START, "ChatNode")
graph.add_conditional_edges("ChatNode", tools_condition)

workflow = graph.compile()

conversation_history = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting the chatbot. Goodbye!")
        break
    # conversation_state = ConversationState(messages=[BaseMessage(content=user_input)])
    response = workflow.invoke({ "messages": [user_input] })
    conversation_history.append({"user": user_input, "bot": response["messages"][-1].content})
    # print("Chatbot:", response)
    
    for msg in conversation_history:
        print(f"You: {msg['user']}")
        print(f"Chatbot: {msg['bot']}")
        print("-" * 20) 