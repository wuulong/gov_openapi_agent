# 政府開放資料 OpenAPI 代理程式 (GovOpenApiAgent)

## 簡介
`GovOpenApiAgent` 是一個基於 Google Agent Development Kit (ADK) 開發的智能代理程式，旨在簡化台灣政府開放資料 API 的使用。透過自然語言，使用者可以查詢並獲取政府各部會提供的開放資料，無需了解複雜的 API 規格和程式碼。

## 主要特色
*   **自然語言互動：** 透過對話式介面，以自然語言向 Agent 提問，獲取所需的政府開放資料。
*   **動態 OpenAPI 整合：** 利用 ADK 的 `OpenAPIToolset`，Agent 能夠動態載入並理解符合 OpenAPI 規範的 API 規格文件，自動生成可呼叫的工具。
*   **可配置的 API 平台：** 透過 `agent_config.yaml` 檔案，您可以輕鬆配置和管理多個政府開放資料平台，包括其 API 規格路徑、認證方式、系統提示等。
*   **彈性的 API Key 管理：** 支援透過 `.env` 檔案安全地管理各平台的 API Key，並由 OpenAPI 工具自動注入。
*   **模組化與可擴展性：** 設計上考慮了未來擴展性，方便持續加入新的部會 API。

## 設定

### 前置條件
*   Python 3.9+
*   pip (Python 套件管理器)

### 安裝
請確保您的 Python 環境已安裝以下套件：

```bash
pip install google-adk python-dotenv pyyaml
```

### 配置

#### `agent_config.yaml`
此檔案位於 `my_samples/gov_openapi_agent/config/agent_config.yaml`，用於定義 Agent 啟用的平台及其詳細配置。

**範例結構：**
```yaml
enable_platform: # 要啟用的平台 ID 列表
  - moenv_platform
  # - isports_platform # 範例：啟用 i運動資訊平台

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
  # - id: isports_platform
  #   name: i運動資訊平台
  #   description: 提供體育活動、體適能證照等資訊。
  #   spec_pathname: i運動資訊平台_openapi.json
  #   enable: false
  #   authentication:
  #     method: none # 假設此範例不需要 API Key
  #   system_prompt: |
  #     你是一個i運動資訊平台的專家。
  #     當使用者詢問體育活動或證照相關問題時，請利用i運動資訊平台提供的工具來查詢資料。
  #   process_tag: sports_data
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
# ... 其他平台的 API Key
```
**請務必將 `your_gemini_api_key` 和 `your_moenv_api_key` 等替換為您實際的 API Key。**

#### `openapi_specs/` 目錄
此目錄位於 `my_samples/gov_openapi_agent/config/openapi_specs/`，用於存放所有政府開放資料的 OpenAPI 規格文件（`.yaml` 或 `.json` 格式）。`agent_config.yaml` 中的 `spec_pathname` 應指向此目錄下的檔案。

## 使用方式
在完成上述配置後，您可以在專案根目錄下執行 `main.py` 來啟動 Agent：

```bash
python my_samples/gov_openapi_agent/main.py
```

Agent 啟動後將進入互動模式，您可以開始輸入查詢。

**範例查詢：**
*   `請給我空氣品質預報資料。` (如果環境部平台已啟用)
*   `查詢i運動資訊平台的體育活動清單。` (如果i運動資訊平台已啟用)

## Agent 架構 (高層次)
1.  **初始化：** Agent 啟動時，首先載入 `.env` 檔案中的環境變數，然後讀取 `agent_config.yaml`。
2.  **動態工具載入：** 根據 `agent_config.yaml` 中 `enable_platform` 列表和 `api_platforms` 的配置，Agent 會動態地載入對應的 OpenAPI 規格文件，並使用 `OpenAPIToolset` 將其轉換為可供 LLM 調用的工具。未啟用的平台將不會載入其工具。
3.  **API Key 注入：** OpenAPI 工具會根據規格文件中定義的安全方案，自動從環境變數中獲取並注入所需的 API Key。
4.  **自然語言處理：** 使用者輸入的自然語言查詢會被傳遞給 LLM (Gemini 2.5 Flash)。
5.  **工具調用：** LLM 根據其指令和可用的工具，判斷是否需要調用特定的 OpenAPI 工具來回答查詢。
6.  **結果回傳：** OpenAPI 工具執行 API 呼叫並返回結果，LLM 將結果整理成自然語言回應給使用者。

---