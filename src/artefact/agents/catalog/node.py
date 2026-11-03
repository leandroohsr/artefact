import logging
from functools import cache

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from artefact.agents.catalog.schema import CatalogOutput
from artefact.agents.catalog.tools import get_active_promotions, search_products
from artefact.agents.common import SpecialistInput, specialist_input, tool_call_budget
from artefact.data.policies import load_policies
from artefact.llm import get_llm
from artefact.prompts import load_prompt

logger = logging.getLogger(__name__)

MAX_TOOL_CALLS = 10


@cache
def build_agent():
    system_prompt = load_prompt("catalog") + "\n\n## Store manual\n\n" + load_policies()
    return create_agent(
        get_llm(),
        tools=[search_products, get_active_promotions],
        system_prompt=system_prompt,
        response_format=CatalogOutput,
        middleware=[tool_call_budget(MAX_TOOL_CALLS)],
    )


class CatalogAgent:
    def __init__(self) -> None:
        """Builds the agent once."""
        self.agent = build_agent()

    def __call__(self, payload: dict) -> dict:
        """LangGraph node. Receives {"task", "messages", "feedback"} via Send; returns {"results": {"catalog": ...}}."""
        output = self.invoke(specialist_input(payload))
        return {"results": {"catalog": output.model_dump()}}

    def invoke(self, input_data: SpecialistInput) -> CatalogOutput:
        logger.debug("===========================")
        logger.debug("CatalogAgent.invoke input_data: %s", input_data)
        logger.debug("===========================")
        result = self.agent.invoke(
            {"messages": [HumanMessage(input_data.model_dump_json())]}
        )
        return result["structured_response"]
