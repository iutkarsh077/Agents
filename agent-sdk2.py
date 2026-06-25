from agents import Agent, Runner
from dotenv import load_dotenv

load_dotenv()


agent1 = Agent(
    name="Issue_Resolver",
    instructions="You are a issue resolver agent, when user aks any query from you, just response with hello world and user name",
    model="gpt-5.4"
)

result = Runner.run_sync(agent1, "Hii my name is Utkarsh")

print(result.final_output)