from langchain.agents import create_agent
from langchain_ollama import ChatOllama

chat_model = ChatOllama(
    model="qwen2.5-coder:7b",
    temperature=0.1,
)

agent = create_agent(model=chat_model)

response = agent.invoke({
    "messages": [
        ("user", "Create a warm greeting.")
    ]
})

print(response["messages"][-1].content)