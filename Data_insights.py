import os
from dotenv import load_dotenv
import langchain
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from Prompts_file import report_prompt
load_dotenv()
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
#this initialize our llm
def initiatellm():
    try:
     llm= ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=GROQ_API_KEY
)
     return llm
    except Exception as e:
     print(f"Error message:{e.message}")
     return None
llm=initiatellm()
def generate_insights(summary:str)->str:
       prompt = PromptTemplate(
       input_variables=["data_summary"],
       template=report_prompt)
       chain=prompt|llm
       response=chain.invoke({"data_summary":summary})
       return response.content

