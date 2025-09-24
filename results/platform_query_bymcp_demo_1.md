M::
Q::# 任務：使用 GovOpenApiAgent MCP 處理使用者提示

您已被配置為 `gov-openapi-agent-mcp` 的客戶端。
您的主要任務是接收使用者輸入（將被視為提示），並將其直接傳遞給指定 MCP 代理程式的 `process_user_prompt` 函數。

## 配置
```toml
[mcp_agent]
name = "gov-openapi-agent-mcp"
function = "process_user_prompt"
```

## 行為
1. 接收使用者輸入。
2. 呼叫 `gov-openapi-agent-mcp` 上的 `process_user_prompt` 函數，並將使用者輸入作為 `prompt` 參數。
3. 將 MCP 代理程式的結果返回給使用者。


/openapi-agent 有哪些平台的開放資料列表
A::```tool_code
print(default_api.process_user_prompt(args={
  "prompt": "/openapi-agent 有哪些平台的開放資料列表"
}))
```
M::
Q::
A::抱歉，我無法透過「平台名稱」進行排序。我只能根據以下欄位進行排序：「ID」、「名稱」、「部門」、「分類」、「更新日期」或「上架日期」。請問您想根據哪個欄位來排序呢？
M::
Q::部門
A::```tool_code
print(default_api.process_user_prompt(args={
  "prompt": "/openapi-agent 有哪些平台的開放資料列表，並依部門排序"
}))
```
M::
Q::使用 /openapi_depts
A::```tool_code
print(default_api.process_user_prompt(args={
  "prompt": "/openapi_depts"
}))
```
M::
Q::
A::好的，我已經列出了目前系統識別到的政府開放資料平台及其 OpenAPI 相關狀態。

請問您對這些資訊有什麼進一步的查詢或操作嗎？
M::
Q::# 任務：使用 GovOpenApiAgent MCP 處理使用者提示

您已被配置為 `gov-openapi-agent-mcp` 的客戶端。
您的主要任務是接收使用者輸入（將被視為提示），並將其直接傳遞給指定 MCP 代理程式的 `process_user_prompt` 函數。

## 配置
```toml
[mcp_agent]
name = "gov-openapi-agent-mcp"
function = "process_user_prompt"
```

## 行為
1. 接收使用者輸入。
2. 呼叫 `gov-openapi-agent-mcp` 上的 `process_user_prompt` 函數，並將使用者輸入作為 `prompt` 參數。
3. 將 MCP 代理程式的結果返回給使用者。


/openapi-agent 使用 openapi_depts, 查地方政府有哪些平台
A::```tool_code
print(default_api.process_user_prompt(args={
  "prompt": "/openapi-agent 使用 openapi_depts, 查地方政府有哪些平台"
}))
```
M::
Q::
A::好的，我已經為您列出了目前系統識別到的地方政府開放資料平台。

請問您對這些地方政府平台有什麼進一步的查詢或操作嗎？
M::
Q::請給我摘要
A::好的，這是地方政府開放資料平台的摘要：

許多地方政府都設有開放資料平台，其中部分平台明確提供了 OpenAPI/Swagger 文件或 UI，例如新北市、桃園市、臺中市、臺南市、高雄市和新竹市。這些平台通常會標示其 OpenAPI 規格版本（如 OAS 2.0 或 OAS 3.0）。

然而，也有相當一部分地方政府的平台，其 OpenAPI 規格狀態顯示為「待確認」，這表示目前系統無法直接取得其 OpenAPI/Swagger 文件的連結，或者這些平台尚未提供標準化的 OpenAPI 文件。有些平台則將其資料整合在全國性的「政府資料開放平臺」中，或主要提供資料集下載而非直接的 API 介接。

總體而言，地方政府在開放資料方面有積極的參與，但 OpenAPI 規格的標準化和可獲取性仍有進步空間。
M::
Q::新竹市平台的資訊
A::好的，這是新竹市政府共通網站管理平台 OpenAPI 的資訊：

*   **平台名稱**：新竹市政府共通網站管理平台 OpenAPI
*   **OpenAPI 規格**：http://webopenapi.hccg.gov.tw/openapi.json
*   **備註**：提供 OpenAPI JSON 文件。
