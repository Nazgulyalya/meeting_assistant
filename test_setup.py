from dotenv import load_dotenv
import os
load_dotenv()

from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
response = llm.invoke("Say hello in one word")
print(response.content)