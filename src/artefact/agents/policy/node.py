import logging
from functools import cache

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from artefact.agents.common import SpecialistInput, specialist_input
from artefact.agents.policy.schema import PolicyOutput
from artefact.data.policies import load_policies
from artefact.llm import get_llm
from artefact.prompts import load_prompt

logger = logging.getLogger(__name__)


@cache
def build_agent():
    system_prompt = load_prompt("policy") + "\n\n## Store manual\n\n" + load_policies()
    return create_agent(
        get_llm(),
        tools=[],
        system_prompt=system_prompt,
        response_format=PolicyOutput,
    )


class PolicyAgent:
    def __init__(self) -> None:
        """Builds the agent once."""
        self.agent = build_agent()

    def __call__(self, payload: dict) -> dict:
        """LangGraph node. Receives {"task", "messages", "feedback"} via Send, returns {"results": {"policy": ...}}."""
        output = self.invoke(specialist_input(payload))
        return {"results": {"policy": output.model_dump()}}

    def invoke(self, input_data: SpecialistInput) -> PolicyOutput:
        logger.debug("===========================")
        logger.debug("PolicyAgent.invoke input_data: %s", input_data)
        logger.debug("===========================")
        result = self.agent.invoke(
            {"messages": [HumanMessage(input_data.model_dump_json())]}
        )
        return result["structured_response"]
