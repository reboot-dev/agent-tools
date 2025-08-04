import asyncio
import logging
from agents.v1.agent_rbt import Agent, Message, Tool
from reboot.aio.applications import Application
from reboot.aio.external import ExternalContext
from servicers import AgentServicer

logging.basicConfig(level=logging.INFO)


async def initialize(context: ExternalContext):
    agent = Agent.ref("test")

    await agent.idempotently().Create(context)

    # response = await agent.idempotently("Invoke #10").Invoke(
    #     context,
    #     messages=[
    #         Message(role="user", content="What is the weather in Copenhagen?"),
    #     ],
    # )

    response = await agent.idempotently().ListTools(context)

    print(f"TOOLS 1: {response}")

    response = await agent.idempotently().Register(
        context, tools=[Tool(name="other")]
    )

    response = await agent.idempotently().ListTools(context)

    print(f"TOOLS 2: {response}")

    await agent.idempotently().Invoke(context, tool_name="triage")

    response = await agent.idempotently().ListTools(context)

    print(f"TOOLS 3: {response}")



async def main():
    await Application(
        servicers=[AgentServicer],
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
