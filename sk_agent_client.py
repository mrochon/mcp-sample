import asyncio
import os

from semantic_kernel.connectors.mcp import MCPStreamableHttpPlugin
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings, AzureAIAgentThread

USER_INPUTS = [
    "Add 1 and 3",
    "Multiply 2 and 5",
    "Get the weather in Seattle",
    "Count the words in this sentence.",
]

async def main():
    # 1. Create the agent
    async with MCPStreamableHttpPlugin(
        name="MathServer",
        description="Sample server for math operations",
        url="http://localhost:8000/mcp/",
        # headers={"Authorization": f"Bearer {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"},
    ) as math_plugin:
        async with (
            DefaultAzureCredential() as creds,
            AzureAIAgent.create_client(credential=creds) as client,
        ):
            agent_definition = await client.agents.create_agent(
                model=AzureAIAgentSettings().model_deployment_name,
                name="MathAgent",
                instructions="Solve algebraic questions using the MCP math server.",
            )
            agent = AzureAIAgent(
                client=client,
                definition=agent_definition,
            )
            thread: AzureAIAgentThread = AzureAIAgentThread(client=client)
            try:
                for user_input in USER_INPUTS:
                    response = await agent.get_response(messages=user_input, thread=thread)
                    print(response)
                    thread = response.thread
            finally:
                await thread.delete() if thread else None
                await client.agents.delete_agent(agent_definition.id) if agent else None
            
if __name__ == "__main__":
    asyncio.run(main())