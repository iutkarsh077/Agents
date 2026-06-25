from typing import Annotated
from agents import Agent, Runner, ToolSearchTool, function_tool, tool_namespace
from dotenv import load_dotenv
import requests
from openai import OpenAI

load_dotenv()


# @function_tool(defer_loading=True)
# def get_customer_profile(
#     customer_id: Annotated[str, "The customer ID to look up."],
# ) -> str:
#     """Fetch a CRM customer profile."""
#     return f"profile for {customer_id}"


# @function_tool(defer_loading=True)
# def list_open_orders(
#     customer_id: Annotated[str, "The customer ID to look up."],
# ) -> str:
#     """List open orders for a customer."""
#     return f"open orders for {customer_id}"


# crm_tools = tool_namespace(
#     name="crm",
#     description="CRM tools for customer lookups.",
#     tools=[get_customer_profile, list_open_orders],
# )


# agent = Agent(
#     name="Operation Assistant",
#     model="gpt-5.4",
#     instructions="Load the crm namespace before using CRM tools.",
#     tools=[*crm_tools, ToolSearchTool()],
# )


# def main():
#     result = Runner.run_sync(agent, "Look up customer_42 and list their open orders.")
#     print(result)

# main()


#######################################################################################################################################

# client = OpenAI()


# @function_tool(defer_loading=True)
# def SearchAllRepositories(username: str):
#     url = f"https://api.github.com/users/{username}/repos"
#     response = requests.get(url=url)

#     github_repository_data = []

#     for d in response.json():
#         info = {
#             "name": d["name"],
#             "description": d["description"],
#             "language": d["language"],
#             "stargazers_count": d["stargazers_count"],
#         }

#         github_repository_data.append(info)

#     return github_repository_data


# @function_tool(defer_loading=True)
# def GetFeedback(githubRepoData: str) -> str:
#     response = client.responses.create(
#         model="gpt-4",
#         instructions="""
#         You are a feedback giver.
#         I will provide GitHub repository information.
#         Give strengths, weaknesses, and suggestions.
#         """,
#         input=f"Give feedback on these repositories:\n{githubRepoData}",
#     )

#     return response.output_text


# tool_connection = tool_namespace(
#     name="github",
#     description="GitHub feedback tools",
#     tools=[GetFeedback, SearchAllRepositories],
# )


# agent = Agent(
#     name="Feedback giver",
#     model="gpt-5.5",
#     instructions="""
#     Give GitHub feedback based on repository information.
#     First fetch repositories, then generate feedback.
#     """,
#     tools=[*tool_connection, ToolSearchTool()],
# )


# def main():
#     result = Runner.run_sync(
#         agent,
#         "Give me GitHub repo feedback for user iutkarsh077",
#     )

#     print(result.final_output)


# if __name__ == "__main__":
#     main()


#######################################################################################################



