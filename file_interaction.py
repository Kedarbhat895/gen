from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv

# Load environment variables
load_dotenv("key.env")

#Text search is difficult hence we are going to introduce embeddings and see the cosine similarity between the user prompt and the fact

text_splitter = CharacterTextSplitter(
    separator = "\n",
    chunk_size=200,
    chunk_overlap=0
)


loader = TextLoader("facts.txt")
documents = loader.load_and_split(text_splitter = text_splitter)

print(documents)

