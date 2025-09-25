# spec 資料的狀況
- 本文件紀錄接入 spec 導入的情況，以提供導入各平台使用與維護的參考。原因是，如果某平台的 spec 遇到導入的問題，表示在維護上，當平台的 spec 變化的時候，再次更新就會遇到問題。也希望將問題能有順便回饋到原來平台，或許有機會當平台更新 spec 時，那些問題能夠被解決，以降低後面 Agentic AI 使用時，遇到問題
- 基本上導入的主要現況會記錄在 config_agent.yaml 中的註解
- 以下是針對有問題的，留下導入經驗

# 修改後可載入
## 環境部環境資料開放平臺
		- status='200'
            - 寫了 python script, 轉換 , fix_openapi_yaml.py
		- 有個 tags: [null] 替換為 tags: []
			- AI 做單一置換
		- moenv_openapi.yaml 文件中執行全域替換
			- 移除所有 default: 9be7b239-557b-4c10-9775-78cadfc555e9。
			- 手動刪除
		- 定義 schema, 拿掉每個 url 中個 key 設定
			- OpenAPIToolset 依賴 OpenAPI 規範中的 securitySchemes 定義來正確識別如何從 AuthCredential 注入 API 金鑰。
			- add_security_to_openapi.py

# 目前遇到問題，無法載入
## 財政部財政資訊中心政府資料開放
- 告知使用者 Swagger 2.0 不兼容性： 解釋 ADK 的 OpenAPI 解析器可能與 Swagger 2.0 規範存在問題，並建議將規範轉換為 OpenAPI 3.x

## 農業部資料開放平台
- fix_openapi_operation_ids.py
- '1000' is not of type 'integer'
    - fix_openapi_default_types.py
- 遇到 schema.description 的問題


# 載入後還有問題
## 中央氣象署開放資料平台
- response 200: to "200"
    - fix_openapi_response_keys.py
- 因為載入有問題，後來轉成 json 格式
- 有 schema.description 的問題, 用以下 code hot fix 後可以載入

```
operation_parser.py line:90
# 如果 'description' 鍵不存在，get() 會返回 None，因此 if not 條件會成立
schema['description'] = description if not schema.get('description') else schema['description']

fix_openapi_security.py

```
- 目前還會遇到
```
Error processing prompt with GovOpenApiAgent: HTTPConnectionPool(host='opendata.cwa.gov.tw', port=80): Max retries exceeded with url: /v1/rest/datastore/F-C0032-001?locationName=%E6%96%B0%E7%AB%B9%E5%B8%82 (Caused by ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x1297d9700>, 'Connection to opendata.cwa.gov.tw timed out. (connect timeout=None)')))

```