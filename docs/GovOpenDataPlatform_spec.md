# 政府開放資料測試平台 API 規格 (GovOpenDataPlatform_spec)

## 簡介
本文件定義了一個用於與 `GovOpenApiAgent` 進行對測的政府開放資料測試平台 API 規格。此平台將作為一個可執行的伺服器，讀取 `opendata_export.csv` 檔案中的資料，並根據 OpenAPI 3.0.x 規範提供 API 服務。其目的在於為 Agent 提供一個穩定、可控且具備真實資料互動能力的測試環境。

## API 功能

### 1. 取得所有開放資料列表
*   **端點:** `GET /opendata`
*   **目的:** 讓 Agent 能夠獲取所有政府開放資料的基本資訊，模擬瀏覽資料集的行為。
*   **查詢參數:**
    *   `limit` (integer, optional): 限制返回的資料筆數，用於分頁。預設值可設定為 100。
    *   `offset` (integer, optional): 跳過指定筆數的資料，用於分頁。預設值為 0。
    *   `sort_by` (string, optional): 排序欄位 (例如：`name`, `department`, `update_date`)。
    *   `order` (string, optional): 排序順序 (`asc` 或 `desc`)。預設值為 `asc`。
*   **回應:**
    *   `200 OK`: 包含開放資料物件陣列的 JSON 格式。
        ```json
        {
          "items": [
            {
              "id": "string",
              "name": "string",
              "department": "string",
              "description": "string",
              "url": "string",
              "category": "string",
              "tags": ["string"],
              "update_date": "string"
            }
          ],
          "total": 0
        }
        ```
    *   `400 Bad Request`: 參數錯誤。

### 2. 搜尋開放資料
*   **端點:** `GET /opendata/search`
*   **目的:** 讓 Agent 能夠根據關鍵字搜尋相關的開放資料，模擬使用者查詢特定主題資料的行為。
*   **查詢參數:**
    *   `query` (string, required): 搜尋關鍵字，可匹配資料名稱、描述、提供單位等。
    *   `department` (string, optional): 依提供單位名稱篩選。
    *   `category` (string, optional): 依資料類別篩選。
    *   `tags` (string, optional): 依標籤篩選 (多個標籤可用逗號分隔)。
    *   `limit` (integer, optional): 限制返回的資料筆數。
    *   `offset` (integer, optional): 跳過指定筆數的資料。
*   **回應:**
    *   `200 OK`: 符合搜尋條件的開放資料物件陣列。
        ```json
        {
          "items": [
            {
              "id": "string",
              "name": "string",
              "department": "string",
              "description": "string",
              "url": "string",
              "category": "string",
              "tags": ["string"],
              "update_date": "string"
            }
          ],
          "total": 0
        }
        ```
    *   `400 Bad Request`: 參數錯誤。

### 3. 取得單一開放資料詳情
*   **端點:** `GET /opendata/{id}`
*   **目的:** 讓 Agent 能夠獲取特定開放資料的完整詳細資訊，模擬查看資料集詳細頁面的行為。
*   **路徑參數:**
    *   `id` (string, required): 開放資料的唯一識別碼。
*   **回應:**
    *   `200 OK`: 單一開放資料物件的 JSON 格式。
        ```json
        {
          "id": "string",
          "name": "string",
          "department": "string",
          "description": "string",
          "url": "string",
          "category": "string",
          "tags": ["string"],
          "update_date": "string",
          "additional_field_1": "string",
          "additional_field_2": "string"
        }
        ```
    *   `404 Not Found`: 未找到指定 ID 的資料。

### 4. 取得開放資料類別列表
*   **端點:** `GET /opendata/categories`
*   **目的:** 讓 Agent 能夠知道有哪些可用的資料類別，以便進行更精確的搜尋或篩選。
*   **回應:**
    *   `200 OK`: 類別名稱的字串陣列。
        ```json
        ["交通", "環境", "水利"]
        ```

### 5. 取得開放資料提供單位列表
*   **端點:** `GET /opendata/departments`
*   **目的:** 讓 Agent 能夠知道有哪些可用的提供單位，以便進行更精確的搜尋或篩選。
*   **回應:**
    *   `200 OK`: 單位名稱的字串陣列。
        ```json
        ["交通部", "環境部", "經濟部水利署"]
        ```

## OpenAPI Spec 結構考量

*   **`info` Object:**
    *   `title`: "政府開放資料測試平台 API"
    *   `description`: "用於與 GovOpenApiAgent 進行對測的政府開放資料測試平台 API。"
    *   `version`: "1.0.0"
*   **`servers` Object:**
    *   `url`: `http://localhost:8000/api/v1` (或根據實際部署調整)
    *   `description`: "測試平台伺服器"
*   **`paths` Object:** 定義上述所有 API 功能的端點及其 HTTP 方法。
*   **`components` Object:**
    *   **`schemas`:**
        *   `OpenDataItem`: 定義開放資料物件的結構，將直接映射 `gov_opendata_platform.db` 中 `open_data_catalog` 資料表的欄位。其包含以下欄位：
            *   `資料集識別碼` (TEXT)
            *   `資料集名稱` (TEXT)
            *   `資料提供屬性` (TEXT)
            *   `服務分類` (TEXT)
            *   `品質檢測` (TEXT)
            *   `檔案格式` (TEXT)
            *   `資料下載網址` (TEXT)
            *   `編碼格式` (TEXT)
            *   `資資料集上架方式` (TEXT)
            *   `資料集描述` (TEXT)
            *   `主要欄位說明` (TEXT)
            *   `提供機關` (TEXT)
            *   `更新頻率` (TEXT)
            *   `授權方式` (TEXT)
            *   `相關網址` (TEXT)
            *   `計費方式` (TEXT)
            *   `提供機關聯絡人姓名` (TEXT)
            *   `提供機關聯絡人電話` (TEXT)
            *   `上架日期` (TEXT)
            *   `詮釋資料更新時間` (TEXT)
            *   `備註` (TEXT)
            *   `資料量` (TEXT)
        *   `OpenDataListResponse`: 包含 `items` (OpenDataItem 陣列) 和 `total` (總筆數) 的回應結構。
        *   `Error`: 定義標準錯誤回應結構 (例如：`code`, `message`)。
    *   **`parameters`:** 定義通用的查詢參數，如 `limit`, `offset`, `query` 等，以便在多個路徑中重複使用。
*   **`tags` Object:** 用於分類 API 端點，例如 `opendata`, `metadata`。

## 資料來源 (`gov_opendata_platform.db`)

*   此 SQLite 資料庫檔案 (`gov_opendata_platform.db`) 將作為測試伺服器的核心資料來源。
*   資料庫中包含 `open_data_catalog` 資料表，其 schema 已在 `OpenDataItem` 中詳細說明。
*   API 的回應將直接從 `open_data_catalog` 資料表中進行 SQL 查詢、篩選、排序和分頁。

## 實作說明 (Python FastAPI)

*   **框架:** 使用 Python FastAPI 框架。
*   **資料處理:** 使用 Python 內建的 `sqlite3` 模組與 `gov_opendata_platform.db` 進行互動。
*   **模型定義:** 使用 Pydantic 定義資料模型，FastAPI 將自動根據這些模型生成 OpenAPI Schema。
*   **自動生成 OpenAPI Spec:** FastAPI 會自動根據定義的路由、Pydantic 模型和 docstrings 生成符合 OpenAPI 3.0.x 規範的 `openapi.json` (或 `openapi.yaml`) 文件，並提供互動式的 Swagger UI (`/docs`) 和 ReDoc UI (`/redoc`)。