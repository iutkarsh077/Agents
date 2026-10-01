from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from tavily import TavilyClient
from typing import Literal
from constant import research_instructions
import os
import subprocess
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def shell_commands(command: str):
    """Run a shell command"""
    
    approval = interrupt({
        "type": "Command Approval",
        "command": command,
        "message": "shell",
    })
    
    if approval != "yes" and approval != "y":
        return "Command not approved"
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=40)
    output = result.stdout
    if result.stderr:
        output += f"\nSTDERR: {result.stderr}"
        
    return output

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
    
checkpoint = InMemorySaver()
main_agent = create_deep_agent(
    name="Researcher",
    tools=[internet_search, shell_commands],
    system_prompt=research_instructions,
    model="gpt-5.4-mini",
    backend=FilesystemBackend(root_dir=".",virtual_mode=True),
    checkpointer=checkpoint
)

config = {
    "configurable": {
        "thread_id": "user123"
    }
}

result = main_agent.invoke({"messages": [{"role": "user", "content": "make a folder of name utkarsh"}]}, config=config)


if "__interrupt__" in result:
    print("Interrupt received, stopping execution.")
    
    msg = result["__interrupt__"][0]
    
    print(msg)
    
    answer = input(f"Do you want to continue? (yes/no): {msg.value["command"]}")
    
    result = main_agent.invoke(
        Command(resume=answer),
        config=config
    )
    
    
print("\n\nFINAL RESULT:")
print(result)