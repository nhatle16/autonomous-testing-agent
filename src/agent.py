from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.tools.read_source import read_input

load_dotenv()

chat_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.1,
    max_output_tokens=200,
)

agent = create_agent(model=chat_model, tools=[read_input])

response = agent.invoke({
    "messages": [
        HumanMessage(content="Create a warm greeting.")
    ]
})

print(response["messages"][-1].content)