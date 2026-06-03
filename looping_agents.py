from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Literal

load_dotenv()

# LLMs
generator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
evaluator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
optimizer_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)


# Main Graph State
class JokeState(BaseModel):
    topic: str
    joke_content: str = ""
    is_approved: Literal["approved", "rejected"] = "rejected"
    iteration: int = 0
    max_iterations: int = 3


class EvaluatorResponse(BaseModel):
    is_approved: Literal["approved", "rejected"] = Field(
        description="Whether the joke is approved or rejected."
    )


structured_evaluator = evaluator_llm.with_structured_output(
    EvaluatorResponse
)

graph = StateGraph(JokeState)


def generate_joke(state: JokeState):
    prompt = f"""
    Generate a funny short joke about {state.topic}.
    """

    result = generator_llm.invoke(prompt)

    print("\n GENERATED JOKE:")
    print(result.content)

    return {
        "joke_content": result.content,
    }


def evaluate_joke(state: JokeState):
    prompt = f"""
    Evaluate this joke.

    Joke:
    {state.joke_content}

    If the joke is funny and makes sense return "approved".
    Otherwise return "rejected".
    """

    result = structured_evaluator.invoke(prompt)

    print("\n EVALUATION:")
    print(result.is_approved)

    return {
        "is_approved": result.is_approved,
        "iteration": state.iteration + 1,
    }


def optimize_joke(state: JokeState):
    prompt = f"""
    Improve this joke and make it funnier:

    {state.joke_content}
    """

    result = optimizer_llm.invoke(prompt)

    print("\n OPTIMIZED JOKE:")
    print(result.content)

    return {
        "joke_content": result.content,
    }


def conditional_edge(state: JokeState):
    current_iteration = state.iteration + 1

    print(f"\n ITERATION: {current_iteration}")

    state.iteration = current_iteration

    if state.is_approved == "approved":
        return "end"

    if current_iteration >= state.max_iterations:
        return "end"

    return "retry"


graph.add_node("generate_joke", generate_joke)
graph.add_node("evaluate_joke", evaluate_joke)
graph.add_node("optimize_joke", optimize_joke)

graph.add_edge(START, "generate_joke")
graph.add_edge("generate_joke", "evaluate_joke")

graph.add_conditional_edges(
    "evaluate_joke",
    conditional_edge,
    {
        "end": END,
        "retry": "optimize_joke",
    },
)

graph.add_edge("optimize_joke", "evaluate_joke")

workflow = graph.compile()

result = workflow.invoke(
    {
        "topic": "programming",
        "max_iterations": 3,
        "iteration": 0,
    }
)

print("\n FINAL RESULT:")
print(result)