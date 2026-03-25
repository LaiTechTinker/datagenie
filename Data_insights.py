import os
from dotenv import load_dotenv
import langchain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv()
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
#this initialize our llm
llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash",
                       temperature=0.7, api_key=GEMINI_API_KEY)

def generate_insights(summary:str)->str:
       prompt = PromptTemplate(
       input_variables=["data_summary"],
       template="""You are a data science expert.

       Analyze the dataset summary below and provide:
       1. Key insights
       2. Data quality issues
       3. Suggestions for cleaning
       4. Potential ML use cases

       Dataset Summary:
       {data_summary}
       """)
       chain=prompt|llm
       response=chain.invoke({"data_summary":summary})
       return response.content

