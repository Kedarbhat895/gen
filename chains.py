from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableMap
import argparse
from dotenv import load_dotenv

load_dotenv("key.env")

parser = argparse.ArgumentParser()
parser.add_argument("--language", help="The programming language for the code", required=True, default="Python")
parser.add_argument("--task", help="What the program should perform", required=True, default="Print any 10 numbers")
args = parser.parse_args()

llm = ChatOpenAI(model_name="gpt-3.5-turbo")

code_prompt = PromptTemplate(template="Write a short function in {language} which will perform {task} and introduce a small bug in it without giving any explanation. Only code is needed", input_variables=["language", "task"])
code_check_prompt = PromptTemplate(template="Given the short piece of code below, find any mistakes/bugs and sanitize it.\nCode:\n{code}", input_variables=["code"])
code_runnable = code_prompt | llm

# Invoke the first runnable to generate code
code_output = code_runnable.invoke({"language": args.language, "task": args.task})

# Step 2: Check and sanitize the generated code using its content
check_runnable = code_check_prompt | llm
check_output = check_runnable.invoke({"code": code_output.content})

print(check_output.content)
