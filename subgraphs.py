from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

load_dotenv()


class SubGraphState(BaseModel):
    inputText: str
    translatedText: str = ""


def TranslateTextToHindi(state: SubGraphState):
    """Translates the input text to Hindi."""
    llm = ChatOpenAI(temperature=0.7, model="gpt-5.4-mini")
    prompt = f"Translate the following text to Hindi: '{state.inputText}'"
    result = llm.invoke(prompt).content
    return {"translatedText": result.strip()}


subgraph = StateGraph(SubGraphState)
subgraph.add_node("TranslateTextHindi", TranslateTextToHindi)
subgraph.add_edge(START, "TranslateTextHindi")
subgraph.add_edge("TranslateTextHindi", END)

subgraph_workflow = subgraph.compile()


class MainGraphState(BaseModel):
    inputText: str
    englishText: str = ""
    hindiText: str = ""


def AskQuestions(state: MainGraphState):
    user_input = state.inputText
    llm = ChatOpenAI(temperature=0.7, model="gpt-5.4-mini")
    result = llm.invoke(user_input).content

    return {"englishText": result}


def TranslateHindiFn(state: MainGraphState):
    result = subgraph_workflow.invoke({"inputText": state.englishText})

    return {"hindiText": result["translatedText"]}


mainGraph = StateGraph(MainGraphState)

mainGraph.add_node("ask", AskQuestions)
mainGraph.add_node("translate", TranslateHindiFn)

mainGraph.add_edge(START, "ask")
mainGraph.add_edge("ask", "translate")
mainGraph.add_edge("translate", END)

mainWorkflow = mainGraph.compile()

ans = mainWorkflow.invoke({"inputText": "What is quantum physics"})

print(ans)
