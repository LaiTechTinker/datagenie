import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from .prompts import report_prompt


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def init_llm():
   
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        api_key=GROQ_API_KEY
    )

llm = init_llm()
def generate_insights(summary: str) -> str:
   
    prompt = PromptTemplate(input_variables=["data_summary"], template=report_prompt)
    chain = prompt | llm
    response = chain.invoke({"data_summary": summary})
    return response.content
