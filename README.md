# LangGraph First Steps

A collection of small, runnable Python scripts for learning [LangGraph](https://langchain-ai.github.io/langgraph/) and related LangChain patterns. Each file focuses on one idea—linear graphs, branching, parallelism, loops, tools, streaming, persistence, subgraphs, and human-in-the-loop (HITL) approval.

## Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys) (most examples call OpenAI models)

## Setup

1. Clone the repository and enter the project directory.

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   **Windows (PowerShell):**

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**

   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install langgraph langchain langchain-openai langchain-community python-dotenv pydantic
   ```

4. Create a `.env` file in the project root (this file is gitignored):

   ```env
   OPENAI_API_KEY=your_key_here
   ```

## Running examples

Run any script directly with Python. Scripts that use OpenAI or interactive input require a valid API key and a terminal session.

```bash
python main2.py
python conditional_agents.py
```

Type `exit` where prompted to quit interactive chat loops.

## Examples overview

| File | Topic | Description |
|------|--------|-------------|
| `main2.py` | Linear graph | Two sequential mock LLM nodes with `MessagesState`. |
| `conditional_agents.py` | Conditional edges | Classifies a query (Math / Code / Text) and routes to a specialized node. |
| `parallel_agents.py` | Parallel execution | Runs multiple essay-evaluation nodes in parallel, then aggregates. |
| `looping_agents.py` | Cycles | Generate → evaluate → optimize joke loop until approved or max iterations. |
| `subgraphs.py` | Subgraphs | Main graph answers in English; nested graph translates to Hindi. |
| `persistance_thread.py` | Checkpointing | Multi-turn chat with `InMemorySaver` and configurable `thread_id`. |
| `streams.py` | Streaming | Same persistence model as above, with `stream_mode="messages"`. |
| `tools1.py` | Tool calling | ReAct-style loop: DuckDuckGo search + custom math tool. |
| `tools2.py` | Tool calling | Research/summary tools with a simple REPL-style chat loop. |
| `hitl.py` | HITL (agent API) | `create_agent` with `HumanInTheLoopMiddleware` for file read/delete approval. |
| `hitl2.py` | HITL (graph + interrupt) | LangGraph `ToolNode` with `interrupt()` inside tools and `Command(resume=...)`. |
| `hitl3.py` | HITL (variant) | Similar to `hitl2.py`; compares interrupt-based approval patterns. |
| `main.py` | Stub | Imports only; use `main2.py` for a minimal runnable graph. |

## Concepts covered

- **StateGraph** — Define state (Pydantic models or `MessagesState`), nodes, and edges.
- **Conditional routing** — `add_conditional_edges` and structured LLM outputs.
- **Parallel fan-out** — Multiple edges from `START` to run nodes concurrently.
- **Loops** — Conditional edges that return to earlier nodes until a stop condition.
- **Subgraphs** — Compile a nested graph and invoke it from a parent node.
- **Persistence** — `InMemorySaver` + `thread_id` in `config["configurable"]` for conversation memory.
- **Streaming** — `workflow.stream(..., stream_mode="messages")` for token-style output.
- **Tools** — `ToolNode`, `tools_condition`, and `@tool` definitions bound to the LLM.
- **Human-in-the-loop** — Middleware-based approval (`hitl.py`) and graph interrupts (`hitl2.py`, `hitl3.py`).

## Project layout

```
.
├── main.py                 # Minimal import stub
├── main2.py                # Hello-world linear graph
├── conditional_agents.py   # Router by query type
├── parallel_agents.py      # Parallel evaluators
├── looping_agents.py       # Iterative joke workflow
├── subgraphs.py            # Nested translation subgraph
├── persistance_thread.py   # Threads + checkpointing
├── streams.py              # Streaming + threads
├── tools1.py               # Search + math tools
├── tools2.py               # Research tools chat
├── hitl.py                 # Agent-level HITL
├── hitl2.py                # Graph interrupt HITL
├── hitl3.py                # Graph interrupt HITL (variant)
├── .env                    # API keys (not committed)
└── .gitignore
```

## Notes

- **Models** — Examples reference models such as `gpt-4`, `gpt-4o-mini`, and `gpt-5.4`. Adjust model names in each file to match what your API key supports.
- **HITL scripts** — `hitl.py`, `hitl2.py`, and `hitl3.py` can read or delete files on disk. Run them only in a safe directory and approve tool calls carefully.
- **requirements.txt** — Listed in `.gitignore`; install packages manually or maintain your own `requirements.txt` locally if you prefer pinned versions.

## License

No license file is included. Add one if you plan to share or publish this repository.
