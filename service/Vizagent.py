from Data_insights import initiatellm
from Prompts_file import VISUALIZATION_PROMPT
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
def generate_chart_spec(user_prompt: str, profile: dict):
    try:
        prompt=PromptTemplate(
            input_variables=["columns", "column_types", "user_prompt"],
            template=VISUALIZATION_PROMPT
        )
        llm=initiatellm()
        parser=StrOutputParser()
        chain=prompt|llm|parser

        response = chain.invoke({
            "columns": profile["columns"],
            "column_types": profile["column_types"],
            "user_prompt": user_prompt
        })

        #  Clean response (remove markdown if any)
        cleaned = response.strip().replace("```json", "").replace("```", "")

        chart_spec = json.loads(cleaned)

        return chart_spec

    except Exception as e:
        print(f"LLM error: {str(e)}")
        return None