from agents.v1.agent_rbt import (
    Agent,
    CallToModelError,
    CreateRequest,
    CreateResponse,
    InvokeRequest,
    InvokeResponse,
    ListToolsRequest,
    ListToolsResponse,
    Message,
    RegisterRequest,
    RegisterResponse,
    Tool,
)
from google.protobuf.json_format import MessageToDict
from langchain.chat_models import init_chat_model
from langchain_core.messages.ai import AIMessage
from rbt.v1alpha1.errors_pb2 import NotFound
from reboot.aio.auth.authorizers import allow
from reboot.aio.contexts import ReaderContext, WorkflowContext, WriterContext
from reboot.aio.workflows import at_least_once

llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")


async def triage():
    print("Calling triage!")


async def other():
    print("Calling other!")


class AgentServicer(Agent.alpha.Servicer):

    def authorizer(self):
        return allow()

    async def Create(
        self,
        context: WriterContext,
        request: CreateRequest,
    ) -> CreateResponse:
        # Add initial tools.
        triage = Tool(name="triage")
        self.state.available_tools.extend([triage])
        self.state.offered_tools.extend([triage])
        return CreateResponse()

    async def ListTools(
        self,
        context: ReaderContext,
        request: ListToolsRequest,
    ) -> ListToolsResponse:
        return ListToolsResponse(tools=self.state.offered_tools)

    async def Invoke(
        self,
        context: WorkflowContext,
        request: InvokeRequest,
    ) -> InvokeResponse:

        # ... middleman for dispatching to the correct tool,
        # specifically for `triage` need to also update which tools we
        # make "offered".

        state = await self.ref().Read(context)

        if request.tool_name not in [tool.name for tool in state.offered_tools]:
            raise Agent.InvokeAborted(
                NotFound(),
                message=f"Tool {request.tool_name} not offered",
            )

        tool = globals()[request.tool_name]

        async def run_tool():
            await tool()

        await at_least_once("Run tool", context, run_tool)

        if request.tool_name == "triage":
            async def offer_available_tools(state):
                state.offered_tools.extend(state.available_tools)

            await self.ref().Write(context, offer_available_tools)

        # async def generate() -> AIMessage:
        #     return await llm.ainvoke(
        #         [MessageToDict(message) for message in request.messages],
        #     )

        # try:
        #     message = await at_most_once(
        #         "Generate", context, generate, type=AIMessage
        #     )
        #     return InvokeResponse(
        #         messages=[Message(role="assistant", content=message.content)]
        #     )
        # except:
        #     import traceback
        #     traceback.print_exc()

        #     # Just bail so that we don't retry this workflow again!
        #     raise Agent.InvokeAborted(CallToModelError())

        return InvokeResponse()

    async def Register(
        self,
        context: WriterContext,
        request: RegisterRequest,
    ) -> RegisterResponse:
        self.state.available_tools.extend(request.tools)
        return RegisterResponse()
