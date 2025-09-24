# 任務：透過 OpenAPI 存取政府開放資料

## 目的
本任務旨在記錄從讀取 OpenAPI 規範到實際呼叫 API 存取政府開放資料的過程與經驗，並作為未來類似任務的參考指南。

## 執行步驟

### 1. 讀取 OpenAPI 規範
- **工具**: `run_shell_command` (使用 `cat` 命令)
- **說明**: 由於 `read_file` 工具可能因檔案過大或格式特殊而截斷內容，建議使用 `cat <file_path>` 搭配 `run_shell_command` 來獲取完整的 OpenAPI JSON 內容。
- **範例**:
  ```bash
  cat /Users/wuulong/github/bmad-pa/specs/政府開放資料測試平台_openapi.json
  ```

### 2. 理解 API 端點與參數
- **工具**: `jq`
- **說明**: 使用 `jq` 解析 OpenAPI JSON 內容，以了解可用的 API 路徑、HTTP 方法、摘要、操作 ID 和所需的參數。
  - **列出所有路徑**:
    ```bash
    cat <openapi_json_file> | jq '.paths | keys[]'
    ```
  - **查看特定端點詳情**:
    ```bash
    cat <openapi_json_file> | jq '.paths["<endpoint_path>"]'
    ```
- **範例**:
  ```bash
  cat /Users/wuulong/github/bmad-pa/specs/政府開放資料測試平台_openapi.json | jq '.paths["/opendata/search"]'
  ```

### 3. 確認正確的參數值
- **工具**: `curl`, `grep`
- **說明**: 對於需要特定值的參數 (例如 `department` 或 `category`)，可以先呼叫相關的 API 端點 (例如 `/opendata/departments` 或 `/opendata/categories`) 來獲取所有可用的值，然後使用 `grep` 進行篩選確認。
- **範例**:
  ```bash
  curl -X GET "http://localhost:8801/opendata/departments" | grep "水利署"
  ```
  (此範例確認到正確的部門名稱應為 "經濟部水利署")

### 4. 實際呼叫 API
- **工具**: `curl`
- **說明**: 根據 OpenAPI 規範和確認後的參數值，建構 `curl` 命令來呼叫目標 API。
- **範例**:
  ```bash
  curl -X GET "http://localhost:8801/opendata/search?query=%E6%B0%B4&department=%E7%B6%93%E6%BF%9F%E9%83%A8%E6%B0%B4%E5%88%A9%E7%BD%B2&limit=10&offset=0"
  ```

### 5. 解讀 API 回應
- **工具**: `jq` (可選)
- **說明**: 分析 API 返回的 JSON 內容，提取所需資訊。如果回應內容複雜，可再次使用 `jq` 進行解析。

## 經驗與教訓
- **檔案讀取問題**: `read_file` 工具在處理單行長 JSON 檔案時，其截斷提示可能不準確。此時應考慮使用 `cat` 命令來確保獲取完整內容。
- **參數精確性**: API 參數值 (特別是名稱) 必須與後端系統中使用的精確字串匹配。透過查詢相關列表端點來驗證參數值是有效的方法。
- **逐步探索**: 從概覽 (所有路徑) 到細節 (特定端點參數)，再到驗證參數值，逐步探索 API 是高效且穩健的策略。

## 相關檔案
- `specs/政府開放資料測試平台_openapi.json`