# 產出整合所有部會開放資料 API 的整體方法論 (修訂版)

## 1. API 盤點與分類標準化
*   **目標：** 建立一個統一的框架來盤點和描述所有部會的開放資料 API。
*   **步驟：**
    *   定義 API 資訊收集的標準欄位，如下方所列。
    *   建立一個中央化的 API 資訊儲存庫（例如：資料庫、YAML/JSON 文件集）。
*   **考量：** 初期聚焦於符合 OpenAPI Specification (Swagger) 規範的單位所提供的 API。

### 1.2 API 規格文件下載與整理技巧

#### 1.2.1 組織架構解析輔助工具

為了更精確地盤點各部會及地方政府的下屬單位，特別是從層級結構化的組織文件中提取第一級子單位，我們開發了 `extract_sub_units.py` 腳本。

*   **工具名稱：** `extract_sub_units.py`
*   **功能：** 從類似 `data/政府組織架構_全.txt` 的樹狀結構文本文件中，根據指定的目標單位名稱，提取其第一級子單位清單。
*   **使用方式：**
    ```bash
    python /Volumes/D2024/github/gov_openapi_agent/extract_sub_units.py [目標單位名稱]
    ```
    *   **範例：** `python /Volumes/D2024/github/gov_openapi_agent/extract_sub_units.py 經濟部` 將列出經濟部下面的第一級子單位。
*   **應用場景：** 當需要從詳細的組織架構文件中，快速識別出可能擁有獨立開放資料平台的下屬行政機關或事業單位時。

在盤點與收集各部會開放資料 API 規格文件的過程中，我們歸納出以下實踐技巧與注意事項：

*   **尋找規格的挑戰與策略：**
    *   **直接搜尋：** 優先嘗試針對特定部會或平台，直接搜尋「[部會名稱] OpenAPI Swagger」或「[平台名稱] OpenAPI Swagger」。
    *   **平台導航：** 若直接搜尋無果，則搜尋「[部會名稱] 開放資料平台」，進入其官方開放資料網站後，尋找「API 專區」、「開發者專區」、「API 文件」、「API 使用說明」等區塊或連結。
    *   **常見路徑猜測與探測：** 許多 Swagger UI 或 OpenAPI 服務會將規格文件放置於可預測的路徑。當直接連結無效時，可嘗試以下路徑：
        *   `[平台基礎URL]/swagger.json`
        *   `[平台基礎URL]/v2/api-docs`
        *   `[平台基礎URL]/openapi.json`
        *   `[平台基礎URL]/openapi.yaml`
        *   `[平台基礎URL]/v3/api-docs` (針對 OpenAPI 3.x)
        *   `[平台基礎URL]/Help` (ASP.NET Web API Help Page)
        *   `[平台基礎URL]/swagger` (常見的 Swagger UI 路徑)
        *   `[平台基礎URL]/api-docs` (常見的 API 文件路徑)
        *   若 `web_fetch` 取得的是 Swagger UI 頁面 (HTML)，由於 `web_fetch` 可能提供摘要內容而非原始 HTML，導致難以直接解析。此時，可嘗試透過 `wget` 下載原始 HTML 內容後，再進行解析，或依賴 `google_web_search` 尋找更直接的規格文件連結。
    *   **Google 搜尋輔助：** 當直接探測無果時，可利用 `google_web_search` 搜尋「[部會名稱] OpenAPI Swagger」等關鍵字，尋找外部文件或社群討論中提及的規格連結。
    *   **認證考量：** 部分 API 即使是規格文件本身，也可能需要認證才能存取（例如 TDX 運輸資料流通服務）。這類情況需在備註中說明。

*   **下載工具：**
    *   **`wget`：** 對於已知直接連結的規格文件，`wget` 是有效且直接的下載工具。
        *   範例：`wget -O specs/[檔名].json [URL]`
    *   **`web_fetch` (用於初步探測)：** 在不確定連結是否為有效規格文件時，可先使用 `web_fetch` 進行內容分析。需注意 `web_fetch` 可能僅提供摘要內容，若需原始內容進行解析，應考慮使用 `wget`。
    *   **使用者提供連結：** 當自動化探測困難時，使用者直接提供正確的規格文件 URL 是最有效率的方式。
    *   **內容驗證與規格確認：** 在將下載的內容保存為規格文件之前，務必進行以下驗證：
        *   **內容類型檢查：** 確認 `web_fetch` 返回的內容是 JSON 或 YAML 格式。
        *   **規格結構驗證：** 使用 `jq` (針對 JSON) 或 `yq` (針對 YAML) 等工具，對內容進行初步解析，確認其是否符合 OpenAPI/Swagger 規格的基本結構。例如，檢查是否存在 `openapi` 或 `swagger` 頂層鍵。

*   **檔案組織與命名規範：**
    *   **統一儲存目錄：** 所有下載的規格文件統一儲存於專案根目錄下的 `specs/` 目錄中。
    *   **命名規範：** 採用一致且具描述性的檔名，建議格式為 `[平台名稱]_openapi.[json/yaml]`，例如 `經濟部水利署水利資料開放平台_openapi.json`。
    *   **備份機制：** 在覆蓋現有規格文件之前，務必先將現有檔案備份至 `specs_tmp/` 目錄，以防誤操作。

*   **資料庫更新與狀態追蹤：**
    *   **`meta_data` 欄位：** 成功下載並驗證的規格文件，應將其檔名記錄於 `openapi_dept` 資料表的 `meta_data` 欄位中，例如 `{"spec_filename": "檔名.json"}`。
    *   **`openapi_spec_url` 欄位：** 若發現更直接或更規範的規格文件 URL，應更新此欄位。
    *   **「待確認」狀態：** 對於未能成功下載或確認規格文件的條目，應在 `openapi_spec_url` 中明確標示為「待確認」，並在 `meta_data` 中記錄失敗原因，例如 `{"spec_download_status": "失敗", "notes": "無法直接從提供的 URL 或常見路徑下載 OpenAPI/Swagger 文件。"}`.
    *   **「規格已下載」狀態：** 新增此狀態，用於表示規格文件已成功下載並通過初步驗證，但尚未進行更深層次的解析與使用。
    *   **「無效資料」狀態：** 新增此狀態，用於表示經過努力後，確認該筆資料無效，無需繼續推動。

### 政府開放資料 API 盤點標準欄位：

1.  **推動狀態 (Promotion Status):**
    *   **說明：** 該開放資料平台或 API 的推動進度或狀態。
    *   **值域：** 「發想 (Ideation)」、「找到規格 (Spec Found)」、「規格已下載 (Spec Downloaded)」、「規格可用 (Spec Usable)」、「認證可用 (Auth pass)」、「單位代理雛形 (Unit Agent Prototype)」、「單位試運行 (Unit Pilot Run)」、「完成 (Completed)」、「無效資料 (Invalid)」
    *   **範例：** 「發想」

    *   **「找到規格 (Spec Found)」：** 已找到 OpenAPI/Swagger 規格文件的 URL，但尚未下載或驗證。
    *   **「規格已下載 (Spec Downloaded)」：** 規格文件已成功從 `openapi_spec_url` 下載到本地，但尚未確認是否可被程式載入解析。
    *   **「規格可用 (Spec Usable)」：** 規格文件已成功下載到本地，並經程式確認可被載入解析，符合 OpenAPI/Swagger 規範。

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

## 5. 整體進展與後續計畫 (Overall Progress and Future Plan)

### 5.1 目前進展
*   已建立政府開放資料 API 清單於 `openapi_dept` 資料庫表格中。
*   已針對部分平台嘗試下載 OpenAPI 規格文件，並記錄嘗試結果。
*   已更新「1.2 API 規格文件下載與整理技巧」章節，納入實務經驗與新策略。

### 5.2 經驗與學習
*   **常見路徑探測：** 針對網站根目錄下的 `swagger.json`, `openapi.json`, `v2/api-docs`, `v3/api-docs`, `/Help`, `/swagger`, `/api-docs` 等常見路徑進行探測是有效的初步策略。
*   **HTML 頁面解析：** 若 `web_fetch` 取得的是 Swagger UI 等 HTML 頁面，需進一步解析 HTML 內容，尋找實際的規格文件 URL (例如，尋找 `configUrl` 或 `url` 參數)。
*   **SPA (Single Page Application) 應用程式的挑戰：** 對於使用 JavaScript 動態載入內容的 SPA 應用程式，OpenAPI 規格可能不會直接嵌入在初始 HTML 中，這增加了直接從 HTML 中提取規格的難度。
*   **多個子單位規格的處理：** 對於單一平台包含多個獨立子單位 OpenAPI 規格的情況（例如新北市政府資料開放平台），若無法找到整合性的規格文件，則應將該平台標記為「無效資料」，並在備註中說明原因。
*   **`web_fetch` 與 `wget` 的使用時機：** `web_fetch` 適合快速獲取網頁摘要以判斷內容類型，但若需完整 HTML 內容進行解析或遇到伺服器阻擋簡單請求時，應使用帶有 User-Agent 的 `wget` 下載完整 HTML。
*   **持續性 404 錯誤或抓取失敗：** 針對特定 URL，即使嘗試多種方法（`web_fetch`、帶 User-Agent 的 `wget`）仍持續出現 404 錯誤或抓取失敗，表示該規格文件可能不存在於該位置，或伺服器主動阻擋存取。此類情況應將該條目標記為「無效資料」。
*   **模糊的 API 文件：** 部分平台提供「API 文件」但未明確指出是否符合 OpenAPI/Swagger 標準。若無明確指示或可發現的規格文件，則難以處理，應將該條目標記為「無效資料」。
*   **Google 搜尋輔助：** 當直接探測無果時，利用 `google_web_search` 搜尋「[部會名稱] OpenAPI Swagger」等關鍵字，尋找外部文件或社群討論中提及的規格連結，此方法在尋找直接規格連結或線索方面非常有效。
*   **詳細記錄：** 每次嘗試的結果，無論成功或失敗，都應詳細記錄於 `openapi_dept` 表格的 `meta_data` 和 `notes` 欄位中，以便追蹤進度並避免重複工作。

### 5.3 後續計畫與優先級
*   **持續盤點：** 按照 `openapi_dept` 表格中的優先級，持續嘗試下載或尋找尚未取得 OpenAPI 規格文件的平台。
*   **優先級策略：**
    1.  優先處理 `promotion_status` 為「找到規格」且 `openapi_spec_url` 顯示為直接連結的條目。
    2.  其次處理 `promotion_status` 為「發想」或「找到規格」，且 `openapi_spec_url` 顯示為 Swagger UI 頁面或有明確線索的條目，嘗試解析 HTML 獲取規格。
    3.  對於 `openapi_spec_url` 仍為「待確認」且無明確線索的條目，可利用 `google_web_search` 進行更廣泛的搜尋。
    4.  對於需要認證才能存取規格文件的平台，暫時擱置，待認證機制建立後再處理。
*   **規格驗證：** 成功下載規格文件後，需進行解析與驗證，確保其符合 Agent 使用要求。
*   **資料庫更新：** 每次成功取得或更新規格文件後，即時更新 `openapi_dept` 表格中的 `promotion_status`、`openapi_spec_url` 和 `meta_data` 欄位。

