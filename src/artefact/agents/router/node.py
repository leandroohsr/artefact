import logging
from functools import cache

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from artefact.agents.common import to_turns
from artefact.agents.router.schema import RouterInput, RouterOutput
from artefact.llm import get_llm
from artefact.prompts import load_prompt

logger = logging.getLogger(__name__)


@cache
def build_agent():
    return create_agent(
        get_llm(),
        tools=[],
        system_prompt=load_prompt("router"),
        response_format=RouterOutput,
    )


class RouterAgent:
    def __init__(self) -> None:
        """Builds the agent once."""
        self.agent = build_agent()

    def __call__(self, state: dict) -> dict:
        """LangGraph node. Splits the latest user message into tasks; returns {"tasks", "out_of_scope"}."""
        output = self.invoke(
            RouterInput(
                history=to_turns(state["messages"][:-1]),
                message=state["messages"][-1].text,
            )
        )
        return {"tasks": output.tasks, "out_of_scope": output.out_of_scope}

    def invoke(self, input_data: RouterInput) -> RouterOutput:
        logger.debug("===========================")
        logger.debug("RouterAgent.invoke input_data: %s", input_data)
        logger.debug("===========================")
        result = self.agent.invoke(
            {"messages": [HumanMessage(input_data.model_dump_json())]}
        )
        return result["structured_response"]
