import logging
import os
import yaml # Import yaml for reading config file
import requests # Added requests import

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm # Keep LiteLlm for now, but model will be fixed to gemini-2.5-flash
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset
from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes, OAuth2Auth, HttpAuth, HttpCredentials # Added HttpAuth, HttpCredentials

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

        enabled_platform_ids = agent_config.get("enable_platform", [])
        api_platforms = agent_config.get("api_platforms", [])

        tools = []
        for platform_config in api_platforms:
            platform_id = platform_config.get("id")
            platform_name = platform_config.get("name", platform_id)
            spec_pathname = platform_config.get("spec_pathname")
            enable_platform = platform_config.get("enable", False)

            if platform_id in enabled_platform_ids and enable_platform and spec_pathname:
                logger.info(f"Loading OpenAPI spec for platform: {platform_name}")

                # Handle authentication
                auth_credential = None
                authentication_config = platform_config.get("authentication", {})
                auth_method = authentication_config.get("method")
                key_env_var = authentication_config.get("key_env_var")

                if auth_method == "api_key" and key_env_var:
                    api_key = os.environ.get(key_env_var)
                    if not api_key:
                        logger.warning(f"API Key for {platform_name} ({key_env_var}) not found in environment variables. API calls might fail.")
                    auth_credential = AuthCredential(auth_type=AuthCredentialTypes.API_KEY, api_key=api_key)
                elif auth_method == "oauth2_client_credentials":
                    client_id_env_var = authentication_config.get("client_id_env_var")
                    client_secret_env_var = authentication_config.get("client_secret_env_var")
                    token_url_env_var = authentication_config.get("token_url_env_var")

                    client_id = os.environ.get(client_id_env_var) if client_id_env_var else None
                    client_secret = os.environ.get(client_secret_env_var) if client_secret_env_var else None
                    token_url = os.environ.get(token_url_env_var) if token_url_env_var else None

                    if not (client_id and client_secret and token_url):
                        logger.warning(f"OAuth2 client credentials for {platform_name} (CLIENT_ID: {client_id_env_var}, CLIENT_SECRET: {client_secret_env_var}, TOKEN_URL: {token_url_env_var}) not fully provided in environment variables. API calls might fail.")
                        auth_credential = None # No credentials if not fully provided
                    else:
                        try:
                            # Manually obtain access token for client credentials flow
                            token_response = requests.post(
                                token_url,
                                data={
                                    "grant_type": "client_credentials",
                                    "client_id": client_id,
                                    "client_secret": client_secret,
                                },
                                timeout=10 # Add a timeout for the request
                            )
                            token_response.raise_for_status() # Raise an exception for HTTP errors
                            access_token = token_response.json().get("access_token")

                            if access_token:
                                auth_credential = AuthCredential(
                                    auth_type=AuthCredentialTypes.HTTP,
                                    http=HttpAuth(
                                        scheme="bearer",
                                        credentials=HttpCredentials(token=access_token),
                                    ),
                                )
                                logger.info(f"Successfully obtained access token for {platform_name}.")
                            else:
                                logger.error(f"Access token not found in response for {platform_name}.")
                                auth_credential = None
                        except requests.exceptions.RequestException as e:
                            logger.error(f"Error obtaining access token for {platform_name}: {e}")
                            auth_credential = None

                # Load OpenAPI Specification
                spec_file_path = os.path.join(os.path.dirname(__file__), "config", "openapi_specs", spec_pathname)
                file_content = None
                try:
                    with open(spec_file_path, "r", encoding="utf-8") as file:
                        file_content = file.read()
                except FileNotFoundError:
                    logger.error(f"Error: The API Spec '{spec_file_path}' for platform '{platform_name}' was not found.")
                    continue # Skip to the next platform

                # Determine spec_str_type (yaml or json)
                spec_str_type = "yaml" if spec_pathname.endswith((".yaml", ".yml")) else "json"

                # Create OpenAPIToolset
                openapi_toolset = OpenAPIToolset(
                    spec_str=file_content,
                    spec_str_type=spec_str_type,
                    auth_credential=auth_credential,
                )
                tools.append(openapi_toolset)
            else:
                logger.info(f"Platform '{platform_name}' (ID: {platform_id}) is not enabled or missing spec_pathname. Skipping.")

        if not tools:
            logger.warning("No OpenAPI tools were loaded based on the configuration.")

        super().__init__(
            name="GovOpenApiAgent", # Renamed agent name
            model="gemini-2.5-flash-lite", # Fixed model as per spec
            instruction=(
                "你是一個能夠查詢政府開放資料的智能助理。"  # You are an intelligent assistant that can query government open data.
                "請根據使用者的自然語言查詢，利用提供的工具來獲取資料。"  # Please use the provided tools to retrieve data based on the user's natural language query.
                "請注意，所有查詢都需要提供 API Key，請確保環境變數已正確配置。" # Please note that all queries require an API Key, please ensure environment variables are correctly configured.
            ),
            description="一個能夠透過 OpenAPI 規範與政府開放資料互動的代理程式。", # General description
            tools=tools, # Dynamically loaded tools
        )