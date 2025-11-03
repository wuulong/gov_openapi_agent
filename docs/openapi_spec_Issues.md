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

schema.setdefault('description', description)
fix_openapi_security.py

```
- 目前還會遇到
```
Error processing prompt with GovOpenApiAgent: HTTPConnectionPool(host='opendata.cwa.gov.tw', port=80): Max retries exceeded with url: /v1/rest/datastore/F-C0032-001?locationName=%E6%96%B0%E7%AB%B9%E5%B8%82 (Caused by ConnectTimeoutError(<urllib3.connection.HTTPConnection object at 0x1297d9700>, 'Connection to opendata.cwa.gov.tw timed out. (connect timeout=None)')))

```

## 新竹市政府資料開放平臺
  File "/Users/wuulong/opt/anaconda3/envs/m2504/lib/python3.12/site-packages/google/adk/tools/openapi_tool/openapi_spec_parser/operation_parser.py", line 90, in _process_operation_parameters                                                                    
    schema.description = (    


附近換成： schema.setdefault('description', description)


INFO:mcp.server.lowlevel.server:Processing request of type CallToolRequest
INFO:__main__:Wuulong:process_user_prompt: {'prompt': '新竹市有哪些方空疏散設施'}
INFO:__main__:Received prompt: 新竹市有哪些方空疏散設施
INFO:__main__:Wuulong:Processing user input: 新竹市有哪些方空疏散設施
INFO:google_adk.google.adk.models.google_llm:Sending out request, model: gemini-2.5-flash-lite, backend: GoogleLLMVariant.GEMINI_
API, stream: False
INFO:google_genai.models:AFC is enabled with max remote calls: 10.
ERROR:__main__:Error processing prompt with GovOpenApiAgent: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': '* Generate
ContentRequest.tools[0].function_declarations[0].name: Invalid function name. 

==>
operationID 需要文字開頭
"operationId": "P3C5FB164814DD7EA",

將 "summary": xxx , "description": xxx 換成 "description"
"description": "取得 新竹市政府1999服務專線熱門問答點閱數統計表",

沒能取得資料
==>
加入：
  "servers": [
    {
      "url": "https://opendata.hccg.gov.tw/API/v3/Rest"
    }
  ],

刪掉：
"host": "opendata.hccg.gov.tw",  "basePath": "/API/v3/Rest",


成功： use: gov-openapi-agent-mcp：新竹市有哪些防空疏散設施
✦ 新竹市共有以下這些防空疏散設施：

   * 新竹市北區崇禮里9鄰中山路296巷1號-B1 (和泰耳鼻喉科)，一般住宅
   * 新竹市北區崇禮里14鄰北大路457號B2 (台新銀行北大分行)，供公眾使用建築物
   * 新竹市北區崇禮里6鄰中山路252號B1 (大樓)，一般住宅
   * 新竹市北區潛園里1鄰西大路417號B1 (合悅都會商旅)，一般住宅
   * 新竹市北區潛園里西大路469巷2號B1 (公寓)，一般住宅
   * 新竹市北區潛園里西大路513號B1 (公寓)，一般住宅
   * 新竹市北區仁德里仁德街50號 (鴻澤北大大樓)，一般住宅
   * 新竹市北區仁德里長安街99號 (公寓)，一般住宅
   * 新竹市北區中央里西門街16號B1 (新竹三信)，供公眾使用建築物
   * 新竹市北區中央里西門街148號B1 (小小天地美語補習班)，供公眾使用建築物