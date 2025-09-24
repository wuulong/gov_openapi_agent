# 政府開放資料 OpenAPI 代理程式 (GovOpenApiAgent)

  

## 簡介

`GovOpenApiAgent` 是一個基於 Google Agent Development Kit (ADK) 開發的智能代理程式，旨在簡化台灣政府開放資料 API 的使用。透過自然語言，使用者可以查詢並獲取政府各部會提供的開放資料，無需了解複雜的 API 規格和程式碼。

- 投影片： [開放 API ADK Agents](https://docs.google.com/presentation/d/1IuZxyZdrvC5dd5BoXDOuZFJXCPFoxErUvg5u5bWNKOM/edit?usp=sharing)

## 緣起
- 既然做了一個環境部的開放資料 API ADK Agent, 那似乎弄更多的政府開放資料平台一起進來，好像也不是個夢
  - [moenv_openapi_agent](https://github.com/wuulong/moenv_openapi_agent)

  

## 主要特色

* **自然語言互動：** 透過對話式介面，以自然語言向 Agent 提問，獲取所需的政府開放資料。

* **動態 OpenAPI 整合：** 利用 ADK 的 `OpenAPIToolset`，Agent 能夠動態載入並理解符合 OpenAPI 規範的 API 規格文件，自動生成可呼叫的工具。

* **可配置的 API 平台：** 透過 `agent_config.yaml` 檔案，您可以輕鬆配置和管理多個政府開放資料平台，包括其 API 規格路徑、認證方式、系統提示等。

* **彈性的 API Key 管理：** 支援透過 `.env` 檔案安全地管理各平台的 API Key，並由 OpenAPI 工具自動注入。

* **模組化與可擴展性：** 設計上考慮了未來擴展性，方便持續加入新的部會 API。

  

## 設定

  

### 前置條件

* Python 3.9+

* pip (Python 套件管理器)

  

### 安裝

請確保您的 Python 環境已安裝以下套件：

  

```bash

pip install google-adk python-dotenv pyyaml

```

  

### 配置

  

#### `agent_config.yaml`

此檔案位於 `config/agent_config.yaml`，用於定義 Agent 啟用的平台及其詳細配置。

  

**範例結構：**

```yaml

enable_platform: # 要啟用的平台 ID 列表

- moenv_platform

- tdx_tranportdata # 範例：啟用交通部運輸資料流通服務平台

- moea_wra_water_data_platform # 範例：啟用經濟部水利署水利資料開放平台

  

api_platforms:

- id: moenv_platform # 此平台的唯一 ID

name: 環境部環境資料開放平臺

description: 提供環境部相關的開放資料，例如空氣品質、酸雨監測等。

spec_pathname: 環境部環境資料開放平臺_openapi.yaml # 相對於 openapi_specs 目錄的路徑

enable: true # 是否啟用此平台 (此旗標作為次要控制，主要控制為 enable_platform)

authentication:

method: api_key # 認證方式：api_key, oauth2, none 等

key_env_var: 環境部環境資料開放平臺_KEY # API Key 的環境變數名稱

system_prompt: |

你是一個環境部開放資料的專家。

當使用者詢問環境相關問題時，請利用環境部提供的工具來查詢資料。

例如：空氣品質、酸雨監測、水質監測等。

process_tag: environment_data # 處理標籤，用於分類或內部邏輯

- id: tdx_tranportdata

name: 交通部運輸資料流通服務平台

description: 提供交通部運輸資料流通服務平台 相關的開放資料，例如公共運輸、觀光、氣象等。

spec_pathname: 交通部運輸資料流通服務平台_openapi.json

enable: false

authentication:

method: oauth2_client_credentials

client_id_env_var: TDX_CLIENT_ID

client_secret_env_var: TDX_CLIENT_SECRET

token_url_env_var: TDX_TOKEN_URL

system_prompt: 你是一個交通部運輸資料流通服務平台的專家。請根據使用者的自然語言查詢，利用提供的工具來獲取資料。

process_tag: tdx_tranportdata

- id: moea_wra_water_data_platform

name: 經濟部水利署水利資料開放平台

description: 提供經濟部水利署水利資料開放平台 相關的開放資料。

spec_pathname: 經濟部水利署水利資料開放平台_openapi.json

enable: false

authentication:

method: none

system_prompt: 你是一個 經濟部水利署水利資料開放平台 的專家。請利用提供的工具來查詢相關資料。

process_tag: moea_wra_water_data_platform

```

  

#### `.env` 檔案

此檔案位於專案根目錄下，用於安全地儲存敏感資訊，例如 API Key。

`GovOpenApiAgent` 會自動載入此檔案中的環境變數。

  

**範例內容：**

```

# Gemini API Key

GEMINI_API_KEY=your_gemini_api_key

  

# OpenAPI Spec API Keys

# 根據 agent_config.yaml 中 api_platforms 的 key_env_var 設定

# 命名規則為 {SPEC_ID}_KEY

環境部環境資料開放平臺_KEY=your_moenv_api_key

I運動資訊平台_KEY=your_isports_api_key

  

# TDX 運輸資料流通服務平台 OAuth2 Client Credentials

TDX_CLIENT_ID=your_tdx_client_id

TDX_CLIENT_SECRET=your_tdx_client_secret

TDX_TOKEN_URL=https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token

# ... 其他平台的 API Key

```

**請務必將 `your_gemini_api_key`、`your_moenv_api_key`、`your_tdx_client_id`、`your_tdx_client_secret` 等替換為您實際的 API Key 或憑證。**

  

#### `openapi_specs/` 目錄

此目錄位於 `config/openapi_specs/`，用於存放所有政府開放資料的 OpenAPI 規格文件（`.yaml` 或 `.json` 格式）。`agent_config.yaml` 中的 `spec_pathname` 應指向此目錄下的檔案。

  

## 使用方式

在完成上述配置後，您可以在專案根目錄下執行 `main.py` 來啟動 Agent：

  

```bash

python main.py

```

  

Agent 啟動後將進入互動模式，您可以開始輸入查詢。

  

**範例查詢：**

* `請給我空氣品質預報資料。` (如果環境部平台已啟用)

* `查詢i運動資訊平台的體育活動清單。` (如果i運動資訊平台已啟用)

  

### Web API (web.py)

`web.py` 提供了一個基於 FastAPI 的 Web 介面，讓您可以透過 HTTP 請求與 `GovOpenApiAgent` 互動。

**運行方式：**

在專案根目錄下執行以下命令來啟動 Web 服務：

```bash
uvicorn web:app --reload --port 8802
```

服務啟動後，您可以在瀏覽器中訪問以下網址來查看 API 文件 (Swagger UI)：

*   **API 文件：** `http://localhost:8802/docs`
*   **API 規格：** `http://localhost:8802/openapi.json`

**如何使用 `/query` 端點：**

您可以向 `http://localhost:8802/query` 發送 POST 請求，並在請求體中包含一個 JSON 對象，其中包含 `prompt` 字段。

**範例 (使用 `curl`)：**

```bash
curl -X POST "http://localhost:8802/query" \
-H "Content-Type: application/json" \
-d '{ "prompt": "請給我空氣品質預報資料。" }'
```

**範例回應：**

```json
{
  "response": "Agent 處理後的結果..."
}
```

## Agent 架構 (高層次)

1. **初始化：** Agent 啟動時，首先載入 `.env` 檔案中的環境變數，然後讀取 `agent_config.yaml`。

2. **動態工具載入：** 根據 `agent_config.yaml` 中 `enable_platform` 列表和 `api_platforms` 的配置，Agent 會動態地載入對應的 OpenAPI 規格文件，並使用 `OpenAPIToolset` 將其轉換為可供 LLM 調用的工具。未啟用的平台將不會載入其工具。

3. **API Key 注入：** OpenAPI 工具會根據規格文件中定義的安全方案，自動從環境變數中獲取並注入所需的 API Key。

4. **自然語言處理：** 使用者輸入的自然語言查詢會被傳遞給 LLM (Gemini 2.5 Flash)。

5. **工具調用：** LLM 根據其指令和可用的工具，判斷是否需要調用特定的 OpenAPI 工具來回答查詢。

6. **結果回傳：** OpenAPI 工具執行 API 呼叫並返回結果，LLM 將結果整理成自然語言回應給使用者。

  

## OpenAPI 規格驗證工具 (`validate_openapi.py`)

此工具用於驗證 `openapi_specs/` 目錄下的 OpenAPI 規格文件是否符合規範。這有助於確保 Agent 能夠正確解析和使用這些規格。

  

### 用途

* 檢查 OpenAPI YAML/JSON 檔案的語法和結構是否正確。

* 識別潛在的驗證錯誤，確保規格文件的品質。

  

### 用法

在專案根目錄下執行以下命令：

  

```bash

python validate_openapi/validate_openapi.py <要檢查的目錄路徑>

```

  

**範例：**

* 驗證 `openapi_specs/` 目錄下的所有規格文件：

```bash

python validate_openapi/validate_openapi.py config/openapi_specs/

```

* 驗證 `my_samples/gov_openapi_agent/validate_openapi/specs/` 目錄下(工作中)的所有規格文件：

```bash

python validate_openapi/validate_openapi.py validate_openapi/specs/

```


## 開放資料 API 清單

- `data/mgr.db`: 儲存 `openapi_dept` 表，此表使用 agentic 環境建構與維護。
- 相關文件：
  - `AI_Open_Data_SDK_Agent_Goal.md`
  - `AI_Open_Data_SDK_Agent_Checklist.md`
  - `AI_Open_Data_SDK_Agent_Methodology.md`
- 功能：
  - 匯出某筆資料成為 YAML 設定。
  - 將 YAML 設定同步回資料庫。
- 包含 `opendata_export1756114029.csv`。


## 測試哪些開放 API 平台

- 預設： API spec load 進來可以，但平台可能需要 Key, 還沒有 key, 所以無法測試
- OK: 有放入 Key 測試過
- 
```
OK 環境部環境資料開放平臺
OK 交通部運輸資料流通服務平台
金管會金融統計資料V2
客家委員會開放資料平台
政府資料標準平臺
財政部財政資訊中心政府資料開放
財政部電子發票整合服務平台
OK 經濟部水利署水利資料開放平台
OK I運動資訊平台
OK 政府開放資料測試平台

```

## 展示 log

- [I運動資訊平台_demo_1.md](results/I運動資訊平台_demo_1.md)
- [both_platform_demo_1.md](results/both_platform_demo_1.md)
- [both_platform_demo_2.md](results/both_platform_demo_2.md)
- [政府開放資料測試平台_demo_1.md](results/政府開放資料測試平台_demo_1.md)
- [客家委員會開放資料平台_demo_1.md](results/客家委員會開放資料平台_demo_1.md)
- [交通部運輸資料流通服務平台_demo_1.md](results/交通部運輸資料流通服務平台_demo_1.md)
- [經濟部水利署水利資料開放平台_demo_1.md](results/經濟部水利署水利資料開放平台_demo_1.md)
- [政府開放資料測試平台_mcp_1.md](results/政府開放資料測試平台_mcp_1.md)

## gov_opendata_platform
- [README.md](gov_opendata_platform/README.md)
  - swagger, openapi 介面查詢開放資料清單
  - cd gov_opendata_platform && uvicorn gov_opendata_platform:app --reload --port 8801
  - 文件： http://localhost:8801/docs
  - spec 下載： http://localhost:8801/openapi.json



## MCP server
- python agent_mcp_server.py --transport sse --port 8800

## MCP client test
- 在 gemini-cli 中測試
- gemini-cli .gemini/settings.json
```
  "mcpServers": {
    "gov-openapi-agent-mcp":{
      "url":"http://127.0.0.1:8800/sse"
    },
  }
```
- sample prompts: （配套的 agent_config.yaml, enable_platform:moenv_platform）
Q::去使用 gov-openapi-agent-mcp Mcp 的 process_user_prompt：有哪些資源回收相關的 api
Q::關於 回收量、回收率 的有哪些
Q::我想知道關於電池的回收量
Q::好的

- result demo: [geminicli-mcp-sse_demo1.md](results/geminicli-mcp-sse_demo1.md)

- 自定義命令，方便指定要下給 agent : [openapi-agent.toml](.gemini/commands/openapi-agent.toml)


## 檔案型開放資料可以回答的 task
- 問之前建議先請 AI 讀一次
- task: [file_based_open_data_method.md](tasks/file_based_open_data_method.md)
