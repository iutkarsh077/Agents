essay = """# Indian Independence

Indias independence is one of the most important events in the history of the country. India got independence from British rule on 15th August 1947 after a long struggle and sacrifice by many brave freedom fighters. This day is celebrated every year as Independence Day.

Before independence, India was ruled by the British for about 200 years. During this period, Indians faced many problems such as heavy taxes, poverty, lack of freedom, and unfair treatment. The British used India’s resources for their own benefit, which made the lives of common people very difficult.

Many great leaders fought for the freedom of India. Mahatma Gandhi played a major role by following the path of truth and non-violence. He started movements like the Non-Cooperation Movement, Civil Disobedience Movement, and Quit India Movement to unite people against British rule. Other freedom fighters such as Subhas Chandra Bose, Bhagat Singh, Jawaharlal Nehru, and Sardar Vallabhbhai Patel also made great sacrifices for the nation.

On 15th August 1947, India finally became an independent nation. Jawaharlal Nehru became the first Prime Minister of independent India and delivered the famous “Tryst with Destiny” speech. The national flag was hoisted, and people celebrated freedom with great joy and pride.

Indian independence teaches us the value of unity, courage, and patriotism. We should respect our freedom fighters and work hard for the progress of our country. Independence is not only about freedom from foreign rule but also about fulfilling our duties as responsible citizens.

India is now one of the largest democracies in the world, and its independence remains a symbol of hope, sacrifice, and national pride.
"""
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class StructuredResponse(BaseModel):
    marks: int = Field(..., description="Marks given to the essay", gt=0, le=10)
    feedback: str = Field(..., description="Feedback for the essay")


structured_model = model.with_structured_output(StructuredResponse)


class EssayEvalutionParameters(BaseModel):
    essay_writing_feedback: str = Field(..., description="Feedback for the essay")
    essay_writing_score: int = Field(
        ..., description="Score for the essay", gt=0, le=10
    )
    writing_score: int = Field(..., description="Marks given to the essay", gt=0, le=10)
    writing_score_reason: str = Field(
        ..., description="Reason for the marks given to the essay"
    )
    sense_of_coherence_score: int = Field(
        ...,
        description="Marks given for the sense of coherence in the essay",
        gt=0,
        le=10,
    )
    sense_of_coherence_score_reason: str = Field(
        ...,
        description="Reason for the marks given for the sense of coherence in the essay",
    )
    overall_score: int = Field(
        ..., description="Overall score for the essay", gt=0, le=10
    )
    overall_score_reason: str = Field(
        ..., description="Reason for the overall score given to the essay"
    )


def evaluate_essay_function(params: EssayEvalutionParameters):
    response = f"Evaluate the following essay and provide feedback, evaluation, and scores for writing and sense of coherence:\n\n{essay}"

    result = structured_model.invoke(response)

    return {
        "essay_writing_feedback": result.feedback,
        "essay_writing_score": result.marks,
    }


def evaluate_sense_of_coherence(params: EssayEvalutionParameters):
    response = f"Evaluate the sense of coherence in the following essay and provide a score and reason:\n\n{essay}"

    result = structured_model.invoke(response)

    return {
        "sense_of_coherence_score": result.marks,
        "sense_of_coherence_score_reason": result.feedback,
    }


def writing_essay_score(params: EssayEvalutionParameters):
    response = f"Evaluate the writing quality of the following essay and provide a score and reason:\n\n{essay}"

    result = structured_model.invoke(response)

    return {"writing_score": result.marks, "writing_score_reason": result.feedback}


def overall_score(params: EssayEvalutionParameters):
    response = f"Based on the evaluation of the essay, provide an overall score and reason:\n\n{essay}"

    result = structured_model.invoke(response)

    return {"overall_score": result.marks, "overall_score_reason": result.feedback}


graph = StateGraph(EssayEvalutionParameters)

graph.add_node("evaluate_essay", evaluate_essay_function)
graph.add_node("evaluate_sense_of_coherence", evaluate_sense_of_coherence)
graph.add_node("writing_essay_score", writing_essay_score)
graph.add_node("overall_score", overall_score)

graph.add_edge(START, "evaluate_essay")
graph.add_edge(START, "evaluate_sense_of_coherence")
graph.add_edge(START, "writing_essay_score")


graph.add_edge("evaluate_essay", "overall_score")
graph.add_edge("evaluate_sense_of_coherence", "overall_score")
graph.add_edge("writing_essay_score", "overall_score")
graph.add_edge("overall_score", END)

graph = graph.compile()

result = graph.invoke(
    {
        "essay_writing_feedback": "",
        "essay_writing_score": 1,
        "writing_score": 1,
        "writing_score_reason": "",
        "sense_of_coherence_score": 1,
        "sense_of_coherence_score_reason": "",
        "overall_score": 1,
        "overall_score_reason": "",
    }
)

print(result)
