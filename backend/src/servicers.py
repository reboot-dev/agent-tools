from agents.v1.agent_rbt import (
    Agent,
    CallToModelError,
    InvokeRequest,
    InvokeResponse,
    Message,
)
from google.protobuf.json_format import MessageToDict
from langchain.chat_models import init_chat_model
from langchain_core.messages.ai import AIMessage
from reboot.aio.auth.authorizers import allow
from reboot.aio.contexts import WorkflowContext
from reboot.aio.workflows import at_most_once

llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")


class AgentServicer(Agent.alpha.Servicer):

    def authorizer(self):
        return allow()

    async def Invoke(
        self,
        context: WorkflowContext,
        request: InvokeRequest,
    ) -> InvokeResponse:

        async def generate() -> AIMessage:
            return await llm.ainvoke(
                [MessageToDict(message) for message in request.messages],
            )

        try:
            message = await at_most_once(
                "Generate", context, generate, type=AIMessage
            )
            return InvokeResponse(
                messages=[Message(role="assistant", content=message.content)]
            )
        except:
            import traceback
            traceback.print_exc()

            # Just bail so that we don't retry this workflow again!
            raise Agent.InvokeAborted(CallToModelError())
