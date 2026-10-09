from dotenv import load_dotenv
from tavily import TavilyClient
import os

from typing import TypedDict, Annotated

from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from db import enqueue1, research_task_collection, sync_client
from langgraph.checkpoint.mongodb import MongoDBSaver
import asyncio

MAX_CONCURRENT_TASKS = 3 
semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)

load_dotenv()


checkpointer = MongoDBSaver(client=sync_client,
    mongo_client=sync_client,
    db_name="user_app",
    collection_name="research_tasks"
)

tavily = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

llm = ChatOpenAI(
    model="gpt-5.4-mini"
)



class State(TypedDict):
    messages: Annotated[list, add_messages]



@tool
def web_search(query: str) -> dict:
    """
    Search the web using Tavily.
    """

    results = tavily.search(
        query=query,
        max_results=10
    )

    return results


tools = [web_search]

llm_with_tools = llm.bind_tools(tools)


def MainAgent(state: State):

    messages = state["messages"]

    system_message = """
You are the main research agent.

Your job is to answer the user's research request.

You have access to a web_search tool.

Use the web_search tool when you need current information,
facts, or external sources.

If you have enough information, provide a final answer.

Do not say that you searched the web unless you actually
used the web_search tool.
"""

    response = llm_with_tools.invoke(
        [
            ("system", system_message),
            *messages
        ]
    )

    return {
        "messages": [response]
    }



tool_node = ToolNode(tools)


def should_use_tool(state: State):

    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    return "planner"


def PlannerAgent(state: State):

    messages = state["messages"]

    prompt = """
You are the research planner.

Look at the conversation and determine whether the main
research agent needs to perform another web search.

Return ONLY one word:

YES
or
NO

Return YES if important information is still missing.

Return NO if enough information has been gathered to
produce the final answer.
"""

    response = llm.invoke(
        [
            ("system", prompt),
            *messages
        ]
    )

    return {
        "messages": [response]
    }



def should_continue(state: State):

    last_message = state["messages"][-1]

    decision = last_message.content.strip().upper()

    if decision == "YES":
        return "main"

    return "end"

graph = StateGraph(State)

graph.add_node("Main", MainAgent)
graph.add_node("Tools", tool_node)
graph.add_node("Planner", PlannerAgent)


graph.add_edge(START, "Main")


graph.add_conditional_edges(
    "Main",
    should_use_tool,
    {
        "tools": "Tools",
        "planner": "Planner"
    }
)


graph.add_edge(
    "Tools",
    "Main"
)


graph.add_conditional_edges(
    "Planner",
    should_continue,
    {
        "main": "Main",
        "end": END
    }
)


workflow = graph.compile(
    checkpointer=checkpointer
)


async def run_single_task(item):
    async with semaphore:
        task_id = item["_id"] 
        thread_id = str(task_id)

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        print("Currently running:", item["task"])

        await research_task_collection.update_one(
            {"_id": task_id},
            {
                "$set": {
                    "status": "in-progress"
                }
            }
        )

        final_answer = ""

        try:

            async for state in workflow.astream(
                {
                    "messages": [
                        HumanMessage(
                            content=item["task"]
                        )
                    ]
                },
                config
            ):

                for node, data in state.items():

                    for message in data.get("messages", []):

                        if node == "Main" and not getattr(message, "tool_calls", None):
                            content = message.content
                            if isinstance(content, str):
                                text = content.strip()
                            elif isinstance(content, list):
                                text_parts = []
                                for part in content:
                                    if isinstance(part, str):
                                        text_parts.append(part)
                                    elif isinstance(part, dict) and "text" in part:
                                        text_parts.append(str(part["text"]))
                                text = "\n".join(text_parts).strip()
                            else:
                                text = str(content).strip()

                            if text:
                                final_answer = text

            # 3. Save final result AFTER graph finishes
            await research_task_collection.update_one(
                {"_id": task_id},
                {
                    "$set": {
                        "status": "completed",
                        "research_data": final_answer
                    }
                }
            )

            print("Research completed:", task_id)

        except Exception as e:

            print("Research failed:", e)

            # Save failure
            await research_task_collection.update_one(
                {"_id": task_id},
                {
                    "$set": {
                        "status": "failed",
                        "error": str(e)
                    }
                }
            )


async def process_research_tasks():
    while enqueue1:
        try:
            item = enqueue1.popleft()
        except IndexError:
            break

        asyncio.create_task(run_single_task(item))