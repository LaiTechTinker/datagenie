import json
from Data_insights import llm
from langchain_core.prompts import PromptTemplate
def generate_chart_spec(user_query: str, columns: list) -> dict:
    prompt = PromptTemplate(
        input_variables=["query", "columns"],
        template="""
You are a data visualization assistant.

Given a user query and dataset columns, return a JSON with:
- chart_type (line, bar, scatter, histogram)
- x_column
- y_column (if applicable)
- aggregation (sum, mean, count, none)

Rules:
- Only use columns provided
- If unclear, choose the best reasonable option

Columns:
{columns}

User Query:
{query}

Return ONLY valid JSON.
"""
    )

    chain = prompt | llm
    response = chain.invoke({
        "query": user_query,
        "columns": columns
    })

    try:
        return json.loads(response.content)
    except:
        raise ValueError("Invalid JSON from LLM:\n" + response.content)