import logging
from functools import cache

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from artefact.agents.common import to_turns
from artefact.agents.delivery.schema import DeliveryInput, DeliveryOutput
from artefact.llm import get_llm
from artefact.prompts import load_prompt

logger = logging.getLogger(__name__)


@cache
def build_agent():
    system_prompt = load_prompt("persona") + "\n\n" + load_prompt("delivery")
    return create_agent(
        get_llm(),
        tools=[],
        system_prompt=system_prompt,
        response_format=DeliveryOutput,
    )


class DeliveryAgent:
    def __init__(self) -> None:
        """Builds the agent once."""
        self.agent = build_agent()

    def __call__(self, state: dict) -> dict:
        """LangGraph node. Writes the reply from tasks, results, out_of_scope and feedback, returns {"draft"}."""
        output = self.invoke(
            DeliveryInput(
                history=to_turns(state["messages"][:-1]),
                message=state["messages"][-1].text,
                tasks=state["tasks"],
                results=state["results"],
                out_of_scope=state["out_of_scope"],
                feedback=state["feedback"],
            )
        )
        return {"draft": output.reply}

    def invoke(self, input_data: DeliveryInput) -> DeliveryOutput:
        logger.debug("===========================")
        logger.debug("DeliveryAgent.invoke input_data: %s", input_data)
        logger.debug("===========================")
        result = self.agent.invoke(
            {"messages": [HumanMessage(input_data.model_dump_json())]}
        )
        return result["structured_response"]
