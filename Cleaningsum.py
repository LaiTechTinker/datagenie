from Data_insights import llm
from langchain_core.prompts import PromptTemplate

def explain_cleaning(report: dict) -> str:
    prompt = PromptTemplate(
        input_variables=["report"],
        template="""
You are a data cleaning expert.

Explain the data issues below in simple, clear terms.

Rules:
- Be concise
- No JSON
- No bullet points unless necessary
- Write like you're explaining to a beginner

Also recommend the best cleaning actions.

Report:
{report}
"""
    )

    chain = prompt | llm
    response = chain.invoke({"report": str(report)})

    return response.content.strip()