import logging
import os
import yaml # Import yaml for reading config file

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm # Keep LiteLlm for now, but model will be fixed to gemini-2.5-flash
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GovOpenApiAgent(LlmAgent):
    def __init__(self): # Removed model_name, api_base, api_key parameters
        # Load agent_config.yaml
        config_path = os.path.join(os.path.dirname(__file__), "config", "agent_config.yaml")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                agent_config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: agent_config.yaml not found at {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing agent_config.yaml: {e}")

        active_api_spec_filename = agent_config.get("active_api_spec")
        enable_active_api = agent_config.get("enable_active_api", False) # Default to False if not specified

        tools = []
        if enable_active_api and active_api_spec_filename:
            # Derive SPEC_ID from filename for API Key
            spec_id = os.path.splitext(active_api_spec_filename)[0]
            # Remove _openapi suffix if present and convert to uppercase with underscores
            if spec_id.endswith("_openapi"):
                spec_id = spec_id[:-len("_openapi")]
            spec_id = spec_id.replace(" ", "_").replace("-", "_").upper()

            api_key_env_var = f"{spec_id}_KEY"
            api_key = os.environ.get(api_key_env_var)

            if not api_key:
                logger.warning(f"API Key for {active_api_spec_filename} ({api_key_env_var}) not found in environment variables. API calls might fail.")
                # Decide whether to raise an error or proceed without key. For now, proceed with warning.

            # Create AuthCredential for the specific API Key
            # Assuming the OpenAPI spec defines security schemes that use 'api_key' in query/header
            # The actual 'name' and 'in' for the API key in the OpenAPI spec will determine how ADK uses it.
            # Here, we just provide the value.
            auth_credential = AuthCredential(auth_type=AuthCredentialTypes.API_KEY, api_key=api_key) if api_key else None

            # Load OpenAPI Specification
            spec_file_path = os.path.join(os.path.dirname(__file__), "config", "openapi_specs", active_api_spec_filename)
            file_content = None
            try:
                with open(spec_file_path, "r", encoding="utf-8") as file:
                    file_content = file.read()
            except FileNotFoundError:
                raise FileNotFoundError(f"Error: The API Spec '{spec_file_path}' was not found as specified in agent_config.yaml.")

            # Determine spec_str_type (yaml or json)
            spec_str_type = "yaml" if active_api_spec_filename.endswith((".yaml", ".yml")) else "json"

            # Create OpenAPIToolset
            openapi_toolset = OpenAPIToolset(
                spec_str=file_content,
                spec_str_type=spec_str_type,
                auth_credential=auth_credential, # Pass the dynamically loaded credential
            )
            tools.append(openapi_toolset)
        else:
            logger.info("No active OpenAPI specification enabled or specified in agent_config.yaml. No OpenAPI tools will be loaded.")

        super().__init__(
            name="GovOpenApiAgent", # Renamed agent name
            model=LlmAgent.model_from_string("gemini-2.5-flash"), # Fixed model as per spec
            instruction=(
                "你是一個能夠查詢政府開放資料的智能助理。"  # You are an intelligent assistant that can query government open data.
                "請根據使用者的自然語言查詢，利用提供的工具來獲取資料。"  # Please use the provided tools to retrieve data based on the user's natural language query.
                "請注意，所有查詢都需要提供 API Key，請確保環境變數已正確配置。" # Please note that all queries require an API Key, please ensure environment variables are correctly configured.
            ),
            description="一個能夠透過 OpenAPI 規範與政府開放資料互動的代理程式。", # General description
            tools=tools, # Dynamically loaded tools
        )