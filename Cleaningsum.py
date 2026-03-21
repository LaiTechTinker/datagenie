from Data_insights import llm
from langchain_core.prompts import PromptTemplate
def explain_cleaning(report: dict) -> str:
    prompt = PromptTemplate(
        input_variables=["report"],
        template="""
You are a data cleaning expert.

Explain the following data issues and suggestions in simple terms.
Also recommend the best actions.

Report:
{report}
"""
    )

    chain = prompt | llm
    response = chain.invoke({"report": str(report)})

    return response.content