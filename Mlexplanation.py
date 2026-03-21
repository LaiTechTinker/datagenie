from Data_insights import llm
from langchain_core.prompts import PromptTemplate

def explain_results(result: dict) -> str:
    prompt = PromptTemplate(
        input_variables=["result"],
        template="""
Explain this machine learning result in simple terms:

{result}

Include:
- what the model means
- how good the performance is
- what the important features imply
"""
    )

    chain = prompt | llm
    response = chain.invoke({"result": str(result)})

    return response.content