# Import necessary libraries
import os
from dotenv import load_dotenv 
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import McpTool, RequiredMcpToolCall, SubmitToolApprovalAction, ToolApproval


# import logging
# logging.basicConfig(level=logging.DEBUG)

load_dotenv()

project_client = AIProjectClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
)

mcp_tool = McpTool(
    server_label="mathserver",
    server_url="http://localhost:8000/MCP",
    allowed_tools=["add", "multiply", "get_weather", "count_words"],  # Include all available tools
)

# You can also add or remove allowed tools dynamically
# search_api_code = "search_azure_rest_api_code"
# mcp_tool.allow_tool(search_api_code)
# print(f"Allowed tools: {mcp_tool.allowed_tools}")

# Create a new agent.
# NOTE: To reuse an existing agent, fetch it with get_agent(agent_id)
with project_client:
    agents_client = project_client.agents

    # Create a new agent.
    # NOTE: To reuse an existing agent, fetch it with get_agent(agent_id)
    agent = agents_client.create_agent(
        model="gpt-4.1-mini",
        name="my-mcp-agent",
        instructions="You are a helpful agent that can use MCP tools to assist users. Use the available MCP tools to answer questions and perform tasks.",
        tools=mcp_tool.definitions,
    )
    
    # Create a thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create a message for the thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Add 1 and 3",
    )
    print(f"Created message, ID: {message.id}")
    
    # Set authentication headers if needed
    mcp_tool.update_headers("SuperSecret", "123456")
    
    # Create and run the agent
    run = agents_client.runs.create(
        thread_id=thread.id, 
        agent_id=agent.id, 
        tool_resources=mcp_tool.resources
    )
    print(f"Created run, ID: {run.id}")
    
    # Process the run and handle tool calls
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id, 
        agent_id=agent.id,
        tool_resources=mcp_tool.resources  # Make sure to include tool resources
    )
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Retrieve the steps taken during the run for analysis
    run_steps = project_client.agents.run_steps.list(thread_id=thread.id, run_id=run.id)

    # Loop through each step to display information
    for step in run_steps:
        print(f"Step {step['id']} status: {step['status']}")

        tool_calls = step.get("step_details", {}).get("tool_calls", [])
        for call in tool_calls:
            print(f"  Tool Call ID: {call.get('id')}")
            print(f"  Type: {call.get('type')}")
            function_details = call.get("function", {})
            if function_details:
                print(f"  Function name: {function_details.get('name')}")
                print(f" function output: {function_details.get('output')}")

        print()
    
    # Fetch and log all messages exchanged during the conversation thread
    messages = project_client.agents.messages.list(thread_id=thread.id)
    print("\nConversation Messages:")
    for msg in messages:
        print(f"Message ID: {msg.id}, Role: {msg.role}")
        if hasattr(msg, 'content') and msg.content:
            for content in msg.content:
                if hasattr(content, 'text') and content.text:
                    print(f"  Content: {content.text.value}")
        print()
        
    # Delete the agent resource to clean up
    project_client.agents.threads.delete(thread.id)
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent and thread")