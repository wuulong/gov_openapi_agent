# 政府開放資料測試平台 API (Gov Open Data Platform API)

## 簡介
此專案是一個基於 FastAPI 框架開發的 API 伺服器，旨在作為 `GovOpenApiAgent` 的測試平台。它模擬了政府開放資料平台的行為，提供了一組 API 端點，用於查詢政府開放資料目錄。資料來源為本地的 SQLite 資料庫 (`gov_opendata_platform.db`)。

## 主要特色
*   **FastAPI 框架:** 使用現代、快速 (高效能) 的 Python Web 框架。
*   **SQLite 資料庫:** 資料儲存於 `gov_opendata_platform.db`，提供持久化和查詢能力。
*   **自動生成 OpenAPI 規格:** FastAPI 自動生成符合 OpenAPI 3.0.x 規範的 API 文件，包含互動式 Swagger UI。
*   **模擬政府開放資料查詢:** 提供資料列表、搜尋、單一資料詳情、類別和提供機關列表等功能。

## 設定

### 前置條件
*   Python 3.9+
*   pip (Python 套件管理器)

### 安裝
1.  導航到 `gov_opendata_platform` 目錄：
    ```bash
    cd gov_opendata_platform
    ```
2.  安裝必要的 Python 套件：
    ```bash
    pip install -r requirements.txt
    ```

### 資料庫
*   本專案預期在 `gov_opendata_platform/` 目錄下存在一個名為 `gov_opendata_platform.db` 的 SQLite 資料庫檔案。
*   資料庫中應包含一個名為 `open_data_catalog` 的資料表，其 schema 應與 `docs/GovOpenDataPlatform_spec.md` 中 `OpenDataItem` 的描述一致。
*   此資料庫應已預先載入政府開放資料目錄的相關數據。

```
CREATE TABLE open_data_catalog (
    資料集識別碼 TEXT,
    資料集名稱 TEXT,
    資料提供屬性 TEXT,
    服務分類 TEXT,
    品質檢測 TEXT,
    檔案格式 TEXT,
    資料下載網址 TEXT,
    編碼格式 TEXT,
    資資料集上架方式 TEXT,
    資料集描述 TEXT,
    主要欄位說明 TEXT,
    提供機關 TEXT,
    更新頻率 TEXT,
    授權方式 TEXT,
    相關網址 TEXT,
    計費方式 TEXT,
    提供機關聯絡人姓名 TEXT,
    提供機關聯絡人電話 TEXT,
    上架日期 TEXT,
    詮釋資料更新時間 TEXT,
    備註 TEXT,
    資料量 TEXT
);

CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE openapi_dept (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    promotion_status TEXT,
    platform_name TEXT NOT NULL,
    department_unit TEXT NOT NULL,
    is_central_unit INTEGER,
    platform_description TEXT,
    website_link TEXT,
    openapi_spec_url TEXT,
    api_endpoint TEXT,
    auth_method TEXT,
    access_notes TEXT,
    meta_data TEXT,
    notes TEXT
);

```

## API 端點

以下是本伺服器提供的主要 API 端點：

*   `GET /opendata`: 取得所有開放資料列表，支援分頁和排序。
*   `GET /opendata/search`: 根據關鍵字、提供機關、服務分類等條件搜尋開放資料。
*   `GET /opendata/{item_id}`: 取得指定 `item_id` 的單一開放資料詳情。
*   `GET /opendata/categories`: 取得所有開放資料的服務分類列表。
*   `GET /opendata/departments`: 取得所有開放資料的提供機關列表。
*   `GET /openapi_depts`: 取得所有 OpenAPI 部門資料列表，支援分頁和排序。
*   `GET /openapi_depts/{dept_id}`: 取得指定 `dept_id` 的單一 OpenAPI 部門詳情。

## 運行伺服器

1.  確保您已在 `gov_opendata_platform` 目錄下。
2.  執行以下命令啟動伺服器：
    ```bash
    uvicorn gov_opendata_platform:app --reload --port 8801
    ```
    伺服器將在 `http://localhost:8801` 運行。

## 訪問 API 文件

伺服器運行後，您可以透過以下網址訪問 API 文件：

*   **Swagger UI (互動式文件):** `http://localhost:8801/docs`
*   **ReDoc UI:** `http://localhost:8801/redoc`
*   **OpenAPI JSON 規格文件:** `http://localhost:8801/openapi.json`

## platform 清單收集
- 平台收集資訊會放在 openapi_dept table, 有時會匯出到 ../data/openapi_dept.csv
- 下載後會放入 ../config/open_specs 中，等待有緣時測試
- 測試時會先用 validate_openapi.py 檢查格式
- 想實際使用時，會添加 config_agent.yaml 成為候選名單，進入帶起階段