from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel

load_dotenv()

class AnswerStructure(BaseModel):
    output_valid: bool
    ai_thoughts: str

model = ChatOpenAI(model="gpt-5.5")
guardrail_model = ChatOpenAI(model="gpt-4o")
structured_output_llm = guardrail_model.with_structured_output(AnswerStructure)

# block_keywords = ["Parrot", "Carrot", "People"]

# def main(query: str):
#     for keywords in block_keywords:
#         if (keywords.lower() in query):
#             print("These keywords are blocked")
#             return
#     response = model.invoke(query)
#     return response.content


# result = main("WHo parrot mahatma gandhi")
# print(result)


messages = [SystemMessage(content="""
        You are a safe assistant.
        Never answer questions about hacking, malware, or illegal activities.
        If asked, politely refuse.
        """)]


def main(query: str):
    messages.append(HumanMessage(content=query))
    checker = structured_output_llm.invoke(messages)
    print(checker)


main("WHo is elon musk")