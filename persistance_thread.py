from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Annotated
from operator import add
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver


load_dotenv()


class PersistenceData(BaseModel):
    content: Annotated[List[str], Field(description="The content of the thread"), add]


llm = ChatOpenAI(temperature=0, model="gpt-4")


def ChatWithUser(state: PersistenceData):
    user_input = state.content[-1]
    response = llm.invoke(
        f"User asked: {user_input}. Please provide a helpful response."
    )
    return {
        "content": [response.content]
    }

graph = StateGraph(PersistenceData)
checkpointer = InMemorySaver()
graph.add_node("ChatWithUser", ChatWithUser)

graph.add_edge(START, "ChatWithUser")
graph.add_edge("ChatWithUser", END)


workflow = graph.compile(checkpointer=checkpointer)
while True:
    user_input = input("You: ")
    thread_id = input("Thread ID (leave blank for new thread): ")
    config = {"configurable": {"thread_id": thread_id}}
    if user_input.lower() == "exit":
        break
    result = workflow.invoke({"content": [user_input]}, config=config)
    print("Thread content:", result)
    print("Workflow history: ", workflow.get_state(config))
