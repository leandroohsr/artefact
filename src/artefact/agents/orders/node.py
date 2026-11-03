import logging
from functools import cache

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from artefact.agents.common import SpecialistInput, specialist_input, tool_call_budget
from artefact.agents.orders.schema import OrdersOutput
from artefact.agents.orders.tools import get_order_status
from artefact.data.policies import load_policies
from artefact.llm import get_llm
from artefact.prompts import load_prompt

logger = logging.getLogger(__name__)


@cache
def build_agent():
    system_prompt = load_prompt("orders") + "\n\n## Store manual\n\n" + load_policies()
    return create_agent(
        get_llm(),
        tools=[get_order_status],
        system_prompt=system_prompt,
        response_format=OrdersOutput,
        # One lookup is enough; the budget stops retries with other spellings of the e-mail or phone.
        middleware=[tool_call_budget(2)],
    )


class OrdersAgent:
    def __init__(self) -> None:
        """Builds the agent once."""
        self.agent = build_agent()

    def __call__(self, payload: dict) -> dict:
        """LangGraph node. Receives {"task", "messages", "feedback"} via Send; returns {"results": {"orders": ...}}."""
        output = self.invoke(specialist_input(payload))
        return {"results": {"orders": output.model_dump()}}

    def invoke(self, input_data: SpecialistInput) -> OrdersOutput:
        logger.debug("===========================")
        logger.debug("OrdersAgent.invoke input_data: %s", input_data)
        logger.debug("===========================")
        result = self.agent.invoke(
            {"messages": [HumanMessage(input_data.model_dump_json())]}
        )
        return result["structured_response"]
