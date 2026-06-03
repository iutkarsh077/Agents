from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Literal, Optional
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)


class StructuredLLMResponse(BaseModel):
    query: str = Field(description="The query to be executed.")
    response: Literal["Math", "Code", "Text"] = Field(
        description="The type of response expected."
    )


structured_model = llm.with_structured_output(StructuredLLMResponse)


class ConditionalAgentType(BaseModel):
    query: str

    type: Optional[Literal["Math", "Code", "Text"]] = None

    response: str = ""


def execute_Query(state: ConditionalAgentType):

    result = structured_model.invoke(state.query)

    return {
        "query": result.query,
        "type": result.response,
    }


def execute_Math(state: ConditionalAgentType):

    prompt = f"Solve this math question: {state.query}"

    result = llm.invoke(prompt)

    return {
        "response": result.content
    }


def execute_Code(state: ConditionalAgentType):

    prompt = f"Solve this coding question: {state.query}"

    result = llm.invoke(prompt)

    return {
        "response": result.content
    }


def execute_Text(state: ConditionalAgentType):

    prompt = f"Answer this text question: {state.query}"

    result = llm.invoke(prompt)

    return {
        "response": result.content
    }


def ConditionalCheck(state: ConditionalAgentType):

    return state.type


graph = StateGraph(ConditionalAgentType)

graph.add_node("execute_Query", execute_Query)
graph.add_node("Math", execute_Math)
graph.add_node("Code", execute_Code)
graph.add_node("Text", execute_Text)

graph.add_edge(START, "execute_Query")

graph.add_conditional_edges(
    "execute_Query",
    ConditionalCheck,
    {
        "Math": "Math",
        "Code": "Code",
        "Text": "Text",
    },
)

graph.add_edge("Math", END)
graph.add_edge("Code", END)
graph.add_edge("Text", END)

app = graph.compile()

result = app.invoke(
    {
        "query": "What is the result of 2 + 2?"
    }
)

print(result)