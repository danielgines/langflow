from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain_community.agent_toolkits.atlassian.toolkit import AtlassianToolkit
from langchain_community.utilities.atlassian import AtlassianAPIWrapper

from langflow.base.agents.agent import LCAgentComponent
from langflow.io import StrInput, SecretStrInput, BoolInput, MultilineInput
from langflow.inputs import HandleInput
from langflow.utils.prompts import ATLASSIAN_AGENT_PROMPT


class AtlassianAgentComponent(LCAgentComponent):
    display_name = "Atlassian Agent"
    description = "Construct a Jira agent from an LLM."
    documentation = "https://python.langchain.com/v0.2/docs/integrations/toolkits/jira/"
    trace_type = "tool"
    beta = True
    icon = "Atlassian"
    name = "Atlassian Agent"

    inputs = LCAgentComponent._base_inputs + [
        HandleInput(
            name="llm",
            display_name="Language Model",
            input_types=["LanguageModel"],
            required=True,
        ),
        MultilineInput(
            name="system_prompt",
            display_name="System Prompt",
            info="System prompt for the agent.",
            value=ATLASSIAN_AGENT_PROMPT,
        ),
        StrInput(
            name="atlassian_instance_url",
            display_name="Site URL",
            required=True,
            info="The base URL of the Confluence Space. Example: https://<company>.atlassian.net/.",
        ),
        StrInput(
            name="atlassian_username",
            display_name="Username",
            required=False,
            info="Atlassian User E-mail. Example: email@example.com",
        ),
        SecretStrInput(
            name="atlassian_api_token",
            display_name="API Key",
            required=True,
            info="Atlassian Key. Create at: https://id.atlassian.com/manage-profile/security/api-tokens",
        ),
        BoolInput(
            name="atlassian_cloud",
            display_name="Use Cloud?",
            required=False,
            value=True,
            advanced=True,
        ),
        StrInput(
            name="filter_keys",
            display_name="Filter Keys",
            required=False,
            info="Comma-separated list of keys to filter from the response.",
        ),
    ]

    def build_agent(self) -> AgentExecutor:
        # Initialize the JiraAPIWrapper with the required parameters
        atlassian_api_wrapper = AtlassianAPIWrapper(
            atlassian_instance_url=self.atlassian_instance_url,
            atlassian_username=self.atlassian_username,
            atlassian_api_token=self.atlassian_api_token,
            atlassian_cloud=self.atlassian_cloud,
            jira=None,
            confluence=None,
            filter_keys=self.filter_keys.split(",") if self.filter_keys else None,
        )

        toolkit = AtlassianToolkit.from_atlassian_api_wrapper(atlassian_api_wrapper)

        agent_args = self.get_agent_kwargs()
        agent_args["max_iterations"] = agent_args["agent_executor_kwargs"]["max_iterations"]
        del agent_args["agent_executor_kwargs"]["max_iterations"]

        system_prompt = self.system_prompt

        # Assuming that the 'input' is a string or a list of string.
        input_text = "\n".join(self.input_value) if isinstance(self.input_value, list) else self.input_value

        messages = [
            ("system", system_prompt),
            ("user", input_text),
        ]

        # Create tool calling agent with prepared messages
        agent = initialize_agent(
            toolkit.get_tools(), self.llm, messages=messages, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, **agent_args
        )

        return agent
