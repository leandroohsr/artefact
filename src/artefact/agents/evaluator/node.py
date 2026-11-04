import logging
from functools import cache

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage

from artefact.agents.common import to_turns
from artefact.agents.evaluator.schema import EvaluatorInput, EvaluatorOutput
from artefact.data.policies import load_policies
from artefact.llm import get_llm
from artefact.prompts import load_prompt

logger = logging.getLogger(__name__)


@cache
def build_agent():
    system_prompt = (
        load_prompt("evaluator")
        + "\n\n## Store persona\n\n"
        + load_prompt("persona")
        + "\n\n## Store manual\n\n"
        + load_policies()
    )
    return create_agent(
        get_llm(),
        tools=[],
        system_prompt=system_prompt,
        response_format=EvaluatorOutput,
    )


class EvaluatorAgent:
    def __init__(self) -> None:
        """Builds the agent once."""
        self.agent = build_agent()

    def __call__(self, state: dict) -> dict:
        """LangGraph node. Reviews the draft, returns {"evaluation"} plus {"messages"} if approved or {"revisions"} if not."""
        output = self.invoke(
            EvaluatorInput(
                history=to_turns(state["messages"][:-1]),
                message=state["messages"][-1].text,
                tasks=state["tasks"],
                results=state["results"],
                out_of_scope=state["out_of_scope"],
                draft=state["draft"],
            )
        )
        if output.approved:
            logger.debug("Draft approved after %s revision(s)", state["revisions"])
            # Only an approved draft becomes part of the conversation history.
            return {"evaluation": output, "messages": [AIMessage(state["draft"])]}
        logger.debug(
            "Draft rejected (revision %s): issues=%s retry_tasks=%s feedback=%s",
            state["revisions"] + 1,
            output.issues,
            output.retry_tasks,
            output.feedback,
        )
        # A retried task replaces the router's task for the same agent, so delivery sees the latest question.
        tasks_by_agent = {}
        for task in state["tasks"]:
            tasks_by_agent[task.agent] = task
        for task in output.retry_tasks:
            tasks_by_agent[task.agent] = task

        return {
            "evaluation": output,
            "feedback": output.feedback,
            "tasks": list(tasks_by_agent.values()),
            "revisions": state["revisions"] + 1,
        }

    def invoke(self, input_data: EvaluatorInput) -> EvaluatorOutput:
        result = self.agent.invoke(
            {"messages": [HumanMessage(input_data.model_dump_json())]}
        )
        return result["structured_response"]
