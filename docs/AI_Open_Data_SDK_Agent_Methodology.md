# 產出整合所有部會開放資料 API 的整體方法論 (修訂版)

## 1. API 盤點與分類標準化
*   **目標：** 建立一個統一的框架來盤點和描述所有部會的開放資料 API。
*   **步驟：**
    *   定義 API 資訊收集的標準欄位，如下方所列。
    *   建立一個中央化的 API 資訊儲存庫（例如：資料庫、YAML/JSON 文件集）。
*   **考量：** 初期聚焦於符合 OpenAPI Specification (Swagger) 規範的單位所提供的 API。

### 1.2 API 規格文件下載與整理技巧

在盤點與收集各部會開放資料 API 規格文件的過程中，我們歸納出以下實踐技巧與注意事項：

*   **尋找規格的挑戰與策略：**
    *   **直接搜尋：** 優先嘗試針對特定部會或平台，直接搜尋「[部會名稱] OpenAPI Swagger」或「[平台名稱] OpenAPI Swagger」。
    *   **平台導航：** 若直接搜尋無果，則搜尋「[部會名稱] 開放資料平台」，進入其官方開放資料網站後，尋找「API 專區」、「開發者專區」、「API 文件」、「API 使用說明」等區塊或連結。
    *   **常見路徑猜測：** 許多 Swagger UI 或 OpenAPI 服務會將規格文件放置於可預測的路徑，例如：
        *   `[平台基礎URL]/swagger.json`
        *   `[平台基礎URL]/v2/api-docs`
        *   `[平台基礎URL]/openapi.json`
        *   `[平台基礎URL]/openapi.yaml`
        *   `[平台基礎URL]/v3/api-docs` (針對 OpenAPI 3.x)
    *   **認證考量：** 部分 API 即使是規格文件本身，也可能需要認證才能存取（例如 TDX 運輸資料流通服務）。這類情況需在備註中說明。

*   **下載工具：**
    *   **`wget`：** 對於已知直接連結的規格文件，`wget` 是有效且直接的下載工具。
        *   範例：`wget -O specs/[檔名].json [URL]`
    *   **`web_fetch` (用於初步探測)：** 在不確定連結是否為有效規格文件時，可先使用 `web_fetch` 進行內容分析，判斷其是否為 JSON/YAML 格式的 OpenAPI/Swagger 規格。

*   **檔案組織與命名規範：**
    *   **統一儲存目錄：** 所有下載的規格文件統一儲存於專案根目錄下的 `specs/` 目錄中。
    *   **命名規範：** 採用一致且具描述性的檔名，建議格式為 `[平台名稱]_openapi.[json/yaml]`，例如 `經濟部水利署水利資料開放平台_openapi.json`。

*   **資料庫更新與狀態追蹤：**
    *   **`meta_data` 欄位：** 成功下載的規格文件，應將其檔名記錄於 `openapi_dept` 資料表的 `meta_data` 欄位中，例如 `{"spec_filename": "檔名.json"}`。
    *   **`openapi_spec_url` 欄位：** 若發現更直接或更規範的規格文件 URL，應更新此欄位。
    *   **「待確認」狀態：** 對於未能成功下載或確認規格文件的條目，應在 `openapi_spec_url` 中明確標示為「待確認」，並在 `meta_data` 中記錄失敗原因，例如 `{"spec_download_status": "失敗", "notes": "無法直接從提供的 URL 或常見路徑下載 OpenAPI/Swagger 文件。"}`.

### 政府開放資料 API 盤點標準欄位：

1.  **推動狀態 (Promotion Status):**
    *   **說明：** 該開放資料平台或 API 的推動進度或狀態。
    *   **值域：** 「發想 (Ideation)」、「找到規格 (Spec Found)」、「規格可用 (Spec Usable)」、「認證可用 (Auth pass)」、「單位代理雛形 (Unit Agent Prototype)」、「單位試運行 (Unit Pilot Run)」、「完成 (Completed)」
    *   **範例：** 「發想」

2.  **開放資料平台名稱 (Open Data Platform Name):**
    *   **說明：** 開放資料平台的簡潔名稱。
    *   **範例：** 「環境部空氣品質開放資料平台」

3.  **部會/單位 (Department/Unit):**
    *   **說明：** 提供此開放資料平台的政府部會或地方政府名稱，可使用樹狀結構表示層級關係。
    *   **範例：** 「經濟部/水利署」、「環境部」、「臺北市政府」

4.  **開放資料平台描述 (Open Data Platform Description):**
    *   **說明：** 簡要說明開放資料平台的主要功能、用途及提供的資料內容。
    *   **範例：** 「提供全國各測站即時空氣品質監測數據，包含 PM2.5、O3 等指標的開放資料平台。」

5.  **網站連結 (Website Link):**
    *   **說明：** 開放資料平台的官方網站連結。
    *   **範例：** `https://data.moenv.gov.tw/`

6.  **OpenAPI Spec 連結 (OpenAPI Spec URL):**
    *   **說明：** 指向平台內各 API 的 Swagger/OpenAPI 規格文件連結。
    *   **範例：** `https://example.gov.tw/api/air_quality/v1/swagger.json`

7.  **API 端點 (Base URL/Endpoint):**
    *   **說明：** API 的基礎 URL，所有資源路徑都將以此為基礎。
    *   **範例：** `https://api.example.gov.tw/air_quality/v1`

8.  **認證方式 (Authentication Method):**
    *   **說明：** API 所需的認證類型。
    *   **選項：** `API Key`, `OAuth2`, `無 (None)`, `其他 (Other)`

9.  **速率限制 (Rate Limit):**
    *   **說明：** API 的呼叫頻率限制，例如每分鐘或每小時可呼叫的次數。
    *   **範例：** 「60 次/分鐘」、「1000 次/小時」

10. **meta_data (JSON):**
    *   **說明：** 額外的元數據，格式為 JSON，具體定義待討論。
    *   **範例：** `{"tags": ["環境", "空氣品質"], "source_system": "環保署資料庫"}`

11. **備註 (Notes):**
    *   **說明：** 任何其他相關的補充說明或特殊注意事項。
*   **建議工具：** `create-knowledge-base-entry` (Data Organizer Agent), `structure-data` (Data Organizer Agent), `write_file`。

## 2. Swagger/OpenAPI 文件解析與驗證機制
*   **目標：** 確保 Agent 能夠自動化地解析、理解並驗證各部會提供的 Swagger/OpenAPI 文件。
*   **初步研究 (基於 Google ADK 相關資訊)：**
    *   **ADK 代理程式與外部文件解析 API 互動的驗證：** 主要關注確保傳遞給 API 的輸入是有效且安全的，以及從 API 接收到的輸出能夠被正確解析和處理。
    *   **OpenAPI 整合：** ADK 能夠透過 OpenAPI 規範 (v3.x) 自動生成可呼叫的工具，這表示 OpenAPI 規範本身就定義了 API 預期的輸入和輸出，可用作驗證的基礎。
    *   **輸入驗證與清理：** 對從大型語言模型 (LLM) 接收到的輸入進行驗證和清理至關重要，以防止惡意注入或模型誤解參數。建議使用 Pydantic 模型進行自動類型驗證，並針對字串輸入使用 `bleach` 或正規表達式等函式庫進行清理。
    *   **輸出解析與驗證：** 當外部文件解析 API 返回響應時，ADK 代理程式的工具需要穩健地解析並驗證該響應。
    *   **安全最佳實踐：** 遵循最小權限原則和參數化工具，避免 LLM 直接構建程式碼。
*   **步驟：**
    *   研究現有的 OpenAPI 解析器庫（例如：Python 的 `openapi-spec-validator` 或 `swagger-parser`），並評估其與 Google ADK 概念的整合潛力。
    *   開發一個模組，能夠讀取 YAML/JSON 格式的 OpenAPI 文件，提取關鍵資訊（端點、參數、回應模型）。
    *   建立驗證規則，檢查文件是否符合 Agent 的使用要求（例如：是否包含足夠的描述、參數類型是否明確），並考慮引入其他堆疊驗證器來強化驗證流程。
*   **建議工具：** `develop-test-scripts` (IT Collaborator Agent), `search-and-recommend-tools` (IT Collaborator Agent)。

## 3. API Key 與認證管理策略
*   **目標：** 設計一個安全、彈性且易於管理的 API Key 儲存和使用機制，並支援多種認證方式。
*   **步驟：**
    *   定義 API Key 的儲存方式（例如：環境變數、加密檔案、安全金鑰管理服務）。
    *   設計 API Key 與部會的綁定關係，並實現個別開關功能。
    *   考量不同 API 的認證流程（例如：OAuth2, Token, Basic Auth）。
*   **建議工具：** `manage-personal-database` (Data Organizer Agent), `draft-document` (Document & Report Specialist Agent)。

## 4. 整體架構設計與文件化
*   **目標：** 將上述所有模組整合起來，形成一個清晰、可擴展的整體架構，並撰寫詳細的方法論文件。
*   **考量：** 自然語言到 API 呼叫的轉換邏輯 (NL2API) 和結果處理與對話生成將由 Google ADK 負責。
*   **步驟：**
    *   繪製系統架構圖（例如：使用 Mermaid）。
    *   撰寫方法論文件，包含設計原則、各模組功能、實作細節、部署考量等。
*   **建議工具：** `outline-presentation` (Document & Report Specialist Agent), `draft-document` (Document & Report Specialist Agent)。
