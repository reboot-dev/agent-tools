import asyncio
import logging
from agents.v1.agent_rbt import Agent, Message
from reboot.aio.applications import Application
from reboot.aio.external import ExternalContext
from servicers import AgentServicer

logging.basicConfig(level=logging.INFO)


async def initialize(context: ExternalContext):
    response = await Agent.ref("test").idempotently("Invoke #9").Invoke(
        context,
        messages=[
            Message(role="user", content="What is the weather in Copenhagen?"),
        ],
    )

    print(response)


async def main():
    await Application(
        servicers=[AgentServicer],
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())
