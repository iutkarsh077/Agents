from langgraph.graph import StateGraph, MessagesState, START, END

def mock_llm(state: MessagesState):
    print(messages := state)
    print("\n\n")
    return {"messages": [{ "role": "ai", "content": "Hello, how can I help you?" }]}


def mock_llm_2(state: MessagesState):
    print(messages := state)
    print("\n\n")
    return {"messages": [{ "role": "ai", "content": "This is a second agent message" }]}

graph = StateGraph(MessagesState)
graph.add_node(mock_llm, "mock_llm")
graph.add_node(mock_llm_2, "mock_llm_2")
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", "mock_llm_2")
graph.add_edge("mock_llm_2", END)

graph = graph.compile()

result = graph.invoke({"messages": [{ "role": "user", "content": "Hi!" }]})

print(result["messages"])