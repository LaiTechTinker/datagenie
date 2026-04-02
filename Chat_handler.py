from Prompts_file import chat_prompt
from Data_insights import initiatellm
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

llm =initiatellm()


def format_memory(memory_list):
    #Convert memory list into readable chat history
    formatted = ""
    for msg in memory_list:
        role = "User" if msg["role"] == "user" else "Assistant"
        formatted += f"{role}: {msg['content']}\n"
    return formatted


def chat_with_report(report_text, user_question, memory):
    chat_prompt = chat_prompt.format(report_text=report_text, chat_history=format_memory(memory), user_question=user_question)

    chain = chat_prompt | llm

    history_text = format_memory(memory)

    response = chain.invoke({
        "report_text": report_text,
        "chat_history": history_text,
        "user_question": user_question
    })

    return response.content