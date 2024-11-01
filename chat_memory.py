from langchain.prompts import HumanMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory,FileChatMessageHistory
from dotenv import load_dotenv

# Load environment variables
load_dotenv("key.env")

# Initialize memory, prompt, and LLM, and save the history in messages.json for storing the context
memory = ConversationBufferMemory(chat_memory = FileChatMessageHistory('messages.json'), memory_key="messages", return_messages=True)
prompt = ChatPromptTemplate(
    input_variables=["content", "messages"],
    messages=[MessagesPlaceholder(variable_name="messages"), HumanMessagePromptTemplate.from_template("{content}")]
)
llm = ChatOpenAI(model_name="gpt-3.5-turbo")

while True:
    content = input('>> ')
    
    # Retrieve conversation history and prepare the prompt
    context = memory.load_memory_variables({})["messages"]
    result = prompt | llm
    
    # Invoke the runnable with both content and context
    response = result.invoke({"content": content, "messages": context})

    # Store the latest user and assistant messages in memory
    memory.save_context({"content": content}, {"content": response.content})
    
    # Print the assistant's response
    print(response.content)
