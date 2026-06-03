from langchain.tools import tool
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from dotenv import load_dotenv
import os

load_dotenv()


checkpointer = InMemorySaver()


@tool
def delete_file(file_path: str) -> str:
    """Deletes a file from the system."""

    try:
        os.remove(file_path)
        return f"File '{file_path}' has been deleted successfully."
    except FileNotFoundError:
        return f"File '{file_path}' not found."
    except Exception as e:
        return f"An error occurred while trying to delete the file: {str(e)}"


@tool
def read_file(file_path: str) -> str:
    """Reads the content of a file."""
    try:
        with open(file_path, "r") as file:
            content = file.read()
            print(f"Content of '{file_path}':\n{content}\n")
        return content
    except FileNotFoundError:
        return f"File '{file_path}' not found."
    except Exception as e:
        return f"An error occurred while trying to read the file: {str(e)}"


hitl = HumanInTheLoopMiddleware(interrupt_on={"delete_file": True, "read_file": True})

config = {"configurable": {"thread_id": "1"}}

agent = create_agent(
    "openai:gpt-5.4",
    tools=[delete_file, read_file],
    middleware=[hitl],
    checkpointer=checkpointer,
)


def main():
    user_input = input("Enter a command (e.g., 'Delete temp.txt' or 'Read temp.txt'): ")
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]}, config=config
    )
    print(result, "\n")

    if "__interrupt__" in result:
        print("Agent requested human intervention for tool execution.\n")
        user_input = input(
            "Agent requested human intervention for tool execution. Please provide the necessary input yes/no: "
        )

        if (
            user_input.lower() == "yes"
            or user_input.lower() == "y"
            or user_input.lower() == "sure"
        ):
            agent.invoke(
                Command(resume={"decisions": [{"type": "approve"}]}), config=config
            )
        else:
            agent.invoke(Command(resume={"decisions": [{"type": "reject"}]}), config=config)



if __name__ == "__main__":
    main()