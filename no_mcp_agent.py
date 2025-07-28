import os, json
from typing import Any, Callable, Set, Dict, List, Optional
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FunctionTool, MessageRole, ToolSet

load_dotenv()

def add(a: int, b: int) -> str:
    """
    Adds a and b and returns the results

    :param a: 1st operand.
    :param a: 2nd operand.    
    :return: Result of addition.
    """
    return f"{a} + {b} = {a + b}"

def multiply(a: int, b: int) -> int:
    """
    Multiplies a and b and returns the results

    :param a: 1st operand.
    :param a: 2nd operand.    
    :return: Result of multiplication.
    """
    return f"{a} * {b} = {a * b}"

# Define user functions
user_functions: Set[Callable[..., Any]] = { add, multiply }

USER_INPUTS = [
    "Add 1 and 3",
    "Multiply 2 and 5",
    "Get the weather in Seattle",
    "Count the words in this sentence.",
]

project_endpoint = os.environ["PROJECT_ENDPOINT"]
project_client = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ["PROJECT_ENDPOINT"],
)

toolset = ToolSet()
functions = FunctionTool(functions=user_functions)
toolset.add(functions)
        
with project_client:
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="helpful_agent",
        instructions="You are a math genius. Use the available tools to answer questions and perform tasks.",
        tools=functions.definitions,
    )
    thread = project_client.agents.threads.create()
    try:
        project_client.agents.enable_auto_function_calls(toolset)
        for user_input in USER_INPUTS:
            message = project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content= user_input,
            )
            run = project_client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
            last_msg = project_client.agents.messages.get_last_message_text_by_role(thread_id=thread.id, role=MessageRole.AGENT)
            if last_msg:
                print(f"Last Message: {last_msg.text.value}")
    except Exception as e:
            print(f"An error occurred: {e}")
    finally:
        project_client.agents.threads.delete(thread.id) if thread else None
        project_client.agents.delete_agent(agent.id) if agent else None
        print("Deleted agent")
        print("Deleted thread")
        print("Finished processing user inputs")


    