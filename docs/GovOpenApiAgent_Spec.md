### **政府開放資料 API SDK Agent 規格 (ADK) - 最終更新版**

**1. Agent 核心資訊**

*   **Agent 名稱：** `GovOpenApiAgent`
*   **Agent 類型：** `LlmAgent(model="gemini-2.5-flash")`
*   **主要指令 (Instruction)：**
    ```
    "你是一個政府開放資料 API 專家，能夠根據使用者的提問，查詢並呼叫政府開放資料 API，並提供相關資訊。你會解析 OpenAPI 規格文件來理解可用的 API，並在呼叫前檢查 API 狀態與取得必要的 API Key。"
    ```
*   **描述 (Description)：**
    ```
    "一個能夠整合並透過自然語言操作政府開放資料 API 的智能代理，旨在降低資料使用門檻並提升效率。"
    ```

**2. 工具 (Tools)**

Agent 將整合以下類型的工具：

*   **動態 OpenAPI 工具 (Dynamic OpenAPI Tools)：**
    *   **目的：** 根據 YAML 設定檔中指定的活躍 API 規格文件，動態生成並註冊對應的 API 呼叫工具。
    *   **實現方式：**
        *   Agent 啟動時，會讀取 YAML 設定檔中的 `active_api_spec` 變數。
        *   同時，會檢查 `agent_config.yaml` 中的 `enable_active_api` 旗標。**如果 `enable_active_api` 為 `false`，則該 OpenAPI 規格文件將不會被載入，也就不會生成對應的工具。**
        *   如果 `enable_active_api` 為 `true`，則載入該變數所指向的 OpenAPI 規格文件，並使用 **`OpenAPIToolset`** 將其轉換為可用的 ADK 工具。
        *   **API Key 處理：** OpenAPI 規格文件本身應定義安全方案 (Security Schemes)，並可配置為從環境變數中自動獲取 API Key。ADK 的 OpenAPI 工具將利用此配置，自動將對應的 `{SPEC_ID}_KEY` 環境變數注入到 API 呼叫中。

**3. 配置 (Configuration)**

*   **環境變數 (`.env`)：**
    *   使用 `.env` 檔案來管理環境變數，**專注於儲存 API Key 相關資訊**。
    *   **API Key：** 每個部會的 API Key 都將獨立存放在 `.env` 中，並遵循 `{SPEC_ID}_KEY` 的命名規則。
        ```
        TRAFFIC_MINISTRY_API_KEY=your_traffic_api_key
        ENVIRONMENTAL_PROTECTION_AGENCY_API_KEY=your_epa_api_key
        GEMINI_API_KEY=your_gemini_api_key
        # ... 其他部會的 API Key
        ```

*   **Agent 設定檔 (`agent_config.yaml`)：**
    *   一個獨立的 YAML 檔案（例如 `config/agent_config.yaml`），用於管理 Agent 的核心配置。
    *   **啟用平台列表 (`enable_platform`)：**
        *   此列表包含 `api_platforms` 中要啟用的平台 `id`。只有在此列表中出現的平台才會被載入和使用。
        ```yaml
        enable_platform: # 要啟用的平台 ID 列表
          - moenv_platform
          - isports_platform # 範例：啟用 i運動資訊平台
        ```
    *   **API 平台配置列表 (`api_platforms`)：**
        *   此列表定義了每個開放資料平台的詳細配置。
        ```yaml
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
          - id: isports_platform
            name: i運動資訊平台
            description: 提供體育活動、體適能證照等資訊。
            spec_pathname: i運動資訊平台_openapi.json
            enable: true
            authentication:
              method: none # 假設此範例不需要 API Key
            system_prompt: |
              你是一個i運動資訊平台的專家。
              當使用者詢問體育活動或證照相關問題時，請利用i運動資訊平台提供的工具來查詢資料。
            process_tag: sports_data
        ```

    *   **資料庫欄位與 YAML 設定對應關係：**
        為了方便管理與動態生成配置，`agent_config.yaml` 中的 `api_platforms` 設定可以從資料庫（例如 `openapi_dept` 表格）中的資料轉換而來。以下是資料庫欄位與 YAML 設定的對應關係範例，以「臺灣物種出現紀錄資料API」為例：

        **資料庫 (`openapi_dept`) 欄位：**
        - `platform_name`: 臺灣物種出現紀錄資料API
        - `platform_description`: 提供 JSON 格式的物種出現紀錄資料。
        - `openapi_spec_url`: 待確認 (需查閱說明文件)
        - `auth_method`: 待確認
        - `meta_data`: {} (此欄位用於儲存額外或非直接對應的 YAML 資訊，以 JSON 格式儲存)

        **對應的 YAML 設定範例：**
        ```yaml
        - id: taiwan_species_occurrence_api # 從 platform_name 轉換而來，或由 meta_data 提供
          name: 臺灣物種出現紀錄資料API # 對應資料庫的 platform_name
          description: 提供 JSON 格式的物種出現紀錄資料。 # 對應資料庫的 platform_description
          spec_pathname: 臺灣物種出現紀錄資料API_openapi.json # 從 meta_data 或 openapi_spec_url 推斷
          enable: false # 從 meta_data 提供，或預設為 false
          authentication:
            method: none # 對應資料庫的 auth_method，若為「待確認」則預設為 none
          system_prompt: 你是一個臺灣物種出現紀錄資料API的專家。請根據使用者的自然語言查詢，利用提供的工具來獲取資料。 # 從 meta_data 提供，或根據 platform_name 生成
          process_tag: taiwan_species_occurrence_api # 從 meta_data 提供，或根據 platform_name 生成
        ```
        **說明：**
        - `id`、`spec_pathname`、`enable`、`system_prompt` 和 `process_tag` 等欄位，若資料庫中 `meta_data` 欄位有對應的 JSON 鍵值，則優先使用 `meta_data` 中的值。
        - 若 `meta_data` 中無對應值，則會根據 `platform_name` 進行推斷（例如 `id` 和 `process_tag`），或使用預設值（例如 `enable: false`）。
        - `authentication.method` 會直接對應 `auth_method` 欄位，若為「待確認」則預設為 `none`。

*   **OpenAPI 規格文件目錄：**
    *   Agent 將監聽一個指定目錄（例如 `config/openapi_specs/`），所有政府開放資料的 OpenAPI `.yaml` 或 `.json` 文件都將放置於此。
    *   Agent 啟動時，會根據 `agent_config.yaml` 中 `enable_platform` 列表和 `api_platforms` 的配置，從此目錄中載入對應的 OpenAPI 規格文件。

**4. 代理工作流程 (Agent Workflow)**

1.  **Agent 初始化：**
    *   **首先，使用 `python-dotenv` 的 `load_dotenv()` 載入 `.env` 檔案，使環境變數在整個 Agent 運行期間可用。**
    *   載入 `agent_config.yaml` 檔案。
    *   **根據 `enable_platform` 列表和 `api_platforms` 配置載入工具：**
        *   遍歷 `api_platforms` 列表。
        *   對於每個平台配置，檢查其 `id` 是否在 `enable_platform` 列表中，並且其自身的 `enable` 旗標為 `true`。
        *   如果滿足條件，則根據 `spec_pathname` 載入對應的 OpenAPI 規格文件。
        *   如果載入成功，則根據 `authentication` 配置創建 `AuthCredential`。
        *   使用 `OpenAPIToolset` 將其轉換為 ADK 工具，並添加到 Agent 的工具列表中。
        *   如果 `enable_platform` 列表中的平台未被啟用或配置錯誤，則不載入其工具，Agent 將無法使用任何外部 API。
2.  **使用者提問：** Agent 接收到使用者的自然語言查詢。
3.  **意圖識別與工具選擇：** LLM 根據其指令和可用的工具描述，分析使用者意圖，並選擇最合適的 OpenAPI 工具來處理查詢。
4.  **前置檢查 (Pre-flight Checks)：**
    *   **此階段不再有獨立的 API Key 或狀態管理工具呼叫。**
    *   如果 Agent 成功載入了 OpenAPI 工具，LLM 將直接呼叫該工具。
    *   API Key 將由 OpenAPI 工具根據其安全配置自動從環境變數中獲取並注入。
5.  **參數提取與工具執行：** LLM 從使用者查詢中提取必要的參數，並呼叫選定的 OpenAPI 工具。
6.  **結果處理：** OpenAPI 工具執行 API 呼叫，並將原始 JSON/XML 結果返回給 Agent。
7.  **回應生成：：** LLM 將 API 呼叫結果轉換為易於理解的自然語言回應，並可選擇性地包含其思考過程和查詢邏輯。

**5. 成功標準與約束條件對應**

*   **取得所有政府開放資料 API 清單：** 透過掃描 `openapi_specs/` 目錄實現。
*   **取得所有開放資料 API 的 YAML 規格文件：** 作為 Agent 的輸入，由使用者提供並放置於指定目錄。
*   **YAML 規格文件合格且 Agent 能解析使用：** 依賴 ADK 的 OpenAPI 工具整合能力，並可能需要額外的驗證步驟。
*   **Agent 具備可調整性：** 透過 `agent_config.yaml` 中的 `api_platforms` 列表實現多個平台的配置和動態載入。
*   **個別開關功能：** 透過 `agent_config.yaml` 中的 `enable_platform` 列表和 `api_platforms` 中各平台的 `enable` 旗標，在 Agent 初始化時控制 OpenAPI 工具的載入。
*   **API Key 管理：** 透過 `.env` 檔案和 OpenAPI 工具的安全配置自動注入。

---