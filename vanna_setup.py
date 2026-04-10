import os
from dotenv import load_dotenv

from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext

from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool
)

from vanna.integrations.sqlite import SqliteRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.integrations.openai import OpenAILlmService

load_dotenv()


class DefaultUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        return User(id="default_user")


async def create_agent():
    # LLM
    llm = OpenAILlmService(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile"
    )

    # Database
    sqlite_runner = SqliteRunner(database_path="clinic.db")

    # Tool registry
    tool_registry = ToolRegistry()

    # Register tools (IMPORTANT: async get_tool)
    await tool_registry.get_tool(RunSqlTool(sqlite_runner))
    await tool_registry.get_tool(VisualizeDataTool())
    await tool_registry.get_tool(SaveQuestionToolArgsTool())
    await tool_registry.get_tool(SearchSavedCorrectToolUsesTool())

    # Memory
    memory = DemoAgentMemory()

    # Agent
    agent = Agent(
        llm_service=llm,
        tool_registry=tool_registry,
        user_resolver=DefaultUserResolver(),
        agent_memory=memory
    )

    return agent