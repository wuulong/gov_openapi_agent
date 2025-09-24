# ADK API 伺服器使用技巧與經驗

## 步驟

### 1. 探索 API 端點

**動作：** 讀取 OpenAPI 規範以了解可用的端點。
**使用工具：** `read_file` (最初)，然後由於截斷問題，改用 `run_shell_command` 搭配 `cat` 來獲取完整內容。
**指令範例：**
```bash
cat api_server_openapi.json
```

**動作：** 從 OpenAPI 規範中列出所有可用的 API 路徑。
**使用工具：** `run_shell_command` 搭配 `jq`。
**指令範例：**
```bash
cat api_server_openapi.json | jq '.paths | keys[]'
```

### 2. 與 API 互動

**動作：** 執行 GET 請求以列出可用的應用程式。
**使用工具：** `run_shell_command` 搭配 `curl`。
**指令範例：**
```bash
curl http://127.0.0.1:8000/list-apps
```
**觀察：** 返回一個包含應用程式名稱的 JSON 陣列。

**動作：** 為特定應用程式和使用者建立新會話。
**使用工具：** `run_shell_command` 搭配 `curl` (POST 請求)。
**端點：** `/apps/{app_name}/users/{user_id}/sessions/{session_id}`
**指令範例：**
```bash
curl -X POST http://127.0.0.1:8000/apps/gov_openapi_agent/users/u_111/sessions/s_112 -H "Content-Type: application/json" -d "{}"
```
**觀察：** 如果會話已存在，API 會返回錯誤 `{"detail":"Session already exists: s_111"}`。成功建立則返回會話詳細資訊。

**動作：** 列出指定應用程式下特定使用者的會話。
**使用工具：** `run_shell_command` 搭配 `curl` (GET 請求)。
**端點：** `/apps/{app_name}/users/{user_id}/sessions`
**指令範例：**
```bash
curl http://127.0.0.1:8000/apps/gov_openapi_agent/users/u_111/sessions
```
**觀察：** 返回指定使用者會話物件的 JSON 陣列。

### 3. 代理程式互動 (伺服器傳送事件 - SSE)

**動作：** 向會話中的代理程式發送訊息並接收串流回應。
**使用工具：** `run_shell_command` 搭配 `curl` (POST 請求至 `/run_sse`)。
**端點：** `/run_sse`
**指令範例：**
```bash
curl -X POST http://127.0.0.1:8000/run_sse \
     -H "Content-Type: application/json" \
     -d "{ \
         \"app_name\": \"gov_openapi_agent\", \
         \"user_id\": \"u_111\", \
         \"session_id\": \"s_111\", \
         \"new_message\": { \
             \"role\": \"user\", \
             \"parts\": [{ \
                 \"text\": \"有哪些部會的開放資料\" \
             }] \
         } \
     }"
```
**觀察：** 輸出由 `data:` 區塊 (SSE) 組成。
*   **函數呼叫：** 代理程式可能會進行 `functionCall` (例如 `get_opendata_departments_opendata_departments_get`) 來滿足請求。
*   **函數回應：** 函數呼叫的結果作為 `functionResponse` 返回。
*   **代理程式的最終回應：** 代理程式處理函數回應並提供自然語言摘要。

## 主要學習/技巧

*   **檔案截斷：** `read_file` 工具可能會截斷大型檔案。對於完整內容，`run_shell_command` 搭配 `cat` 是一個可靠的替代方案。
*   **會話管理：** 請注意會話是否存在。嘗試建立已存在的會話將導致錯誤。
*   **代理程式能力：** ADK API 伺服器允許代理程式解釋自然語言查詢，執行工具呼叫（在其 OpenAPI 規範中定義的函數），並根據工具輸出合成回應。
*   **SSE 用於串流：** `run_sse` 端點對於與代理程式進行即時、串流互動至關重要，它顯示了函數呼叫和回應等中間步驟。
