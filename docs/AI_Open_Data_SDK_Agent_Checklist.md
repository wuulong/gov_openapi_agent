# 政府開放資料 API SDK Agent 目標達成檢查清單

## 核心目標達成
- [ ] 能夠取得所有政府開放資料 API 的清單。
- [ ] 能夠取得所有開放資料 API 的 YAML (或 Swagger/OpenAPI) 規格文件。
- [ ] 取得的 YAML 規格文件是合格的，且 Agent 能夠正確解析並使用。
- [ ] Agent 具備可調整性，能夠持續加入新的部會 API。
- [ ] 產出整合所有部會開放資料 API 的整體方法論。
- [ ] 產出並完成一個部會開放資料 API 的整合方法論（作為範例或最小可行產品）。

## 約束條件符合性
- [ ] 實現個別開關功能，能夠獨立控制每個部會 API 的啟用/停用。
- [ ] 實現 API Key 管理功能，能夠設定和管理每個部會 API 所需的 API Key。

## 平台盤點進度追蹤 (Platform Inventory Progress Tracking)

為了確保所有目標平台都能被有效盤點，我們將維護一個平台清單，並依據其 OpenAPI 規格文件的獲取狀態進行分類追蹤。此清單將動態生成，並反映 `openapi_dept` 資料庫表格中的最新狀態。

### 追蹤分類：

1.  **已完成 (Completed)：**
    *   **定義：** 該平台的 OpenAPI 規格文件已成功獲取、驗證，並已準備好供 Agent 使用。
    *   **對應 `promotion_status`：** 「規格可用 (Spec Usable)」、「認證可用 (Auth pass)」、「單位代理雛形 (Unit Agent Prototype)」、「單位試運行 (Unit Pilot Run)」、「完成 (Completed)」。

2.  **確認沒有 (Confirmed Not Available)：**
    *   **定義：** 經過多方嘗試與確認，該平台目前未提供 OpenAPI 規格文件，或其提供的 API 不符合盤點範疇。
    *   **對應 `promotion_status`：** 「無效資料 (Invalid)」。

3.  **待處理 (Pending)：**
    *   **定義：** 該平台仍在盤點過程中，其 OpenAPI 規格文件尚未完全獲取或驗證。
    *   **對應 `promotion_status`：** 「發想 (Ideation)」、「找到規格 (Spec Found)」、「規格已下載 (Spec Downloaded)」。

### 清單結構 (範例)：

```
- [平台名稱] (部會/單位) - [目前狀態] - [備註]
```

**範例說明：**
*   **已完成：**
    *   [環境部環境資料開放平臺] (環境部) - 已完成 - 規格文件已成功整合。
*   **確認沒有：**
    *   [國防部開放檔案實名制申請資訊 API] (國防部) - 確認沒有 - 無法獲取 OpenAPI 規格文件。
*   **待處理 (Pending)：**
    *   **中央政府部會：**
        - [ ] 行政院 (Executive Yuan)
        - [ ] 內政部 (Ministry of Interior)
        - [ ] 外交部 (Ministry of Foreign Affairs)
        - [ ] 國防部 (Ministry of National Defense)
        - [ ] 財政部 (Ministry of Finance)
        - [ ] 教育部 (Ministry of education)
        - [ ] 法務部 (Ministry of Justice)
        - [ ] 經濟部 (Ministry of Economic Affairs)
            - [ ] 經濟部標準檢驗局
            - [ ] 經濟部智慧財產局
            - [ ] 經濟部水利署
            - [ ] 經濟部商業發展署
            - [ ] 經濟部產業發展署
            - [ ] 經濟部國際貿易署
            - [ ] 經濟部能源署
            - [ ] 經濟部中小及新創企業署
            - [ ] 經濟部產業園區管理局
            - [ ] 經濟部地質調查及礦業管理中心
        - [ ] 交通部 (Ministry of Transportation and Communications)
        - [ ] 勞動部 (Ministry of Labor)
        - [ ] 衛生福利部 (Ministry of Health and Welfare)
        - [ ] 文化部 (Ministry of Culture)
        - [ ] 農業部 (Ministry of Agriculture)
        - [ ] 環境部 (Ministry of Environment)
        - [ ] 數位發展部 (Ministry of Digital Affairs)
        - [ ] 金融監督管理委員會 (Financial Supervisory Commission)
        - [ ] 國家發展委員會 (National Development Council)
        - [ ] 國家科學及技術委員會 (National Science and Technology Council)
        - [ ] 海洋委員會 (Ocean Affairs Council)
        - [ ] 僑務委員會 (Overseas Community Affairs Council)
        - [ ] 國軍退除役官兵輔導委員會 (Veterans Affairs Council)
        - [ ] 原住民族委員會 (Council of Indigenous Peoples)
        - [ ] 客家委員會 (Hakka Affairs Council)
        - [ ] 行政院公共工程委員會 (Public Construction Commission, Executive Yuan)
        - [ ] 中央選舉委員會 (Central Election Commission)
        - [ ] 公平交易委員會 (Fair Trade Commission)
        - [ ] 國家通訊傳播委員會 (National Communications Commission)
        - [ ] 行政院主計總處 (Directorate-General of Budget, Accounting and Statistics, Executive Yuan)
        - [ ] 行政院人事行政總處 (Directorate-General of Personnel Administration, Executive Yuan)
        - [ ] 中央銀行 (Central Bank of the Republic of China (Taiwan))
        - [ ] 國立故宮博物院 (National Palace Museum)
        - [ ] 中央氣象署 (Central Weather Administration)
        - [ ] 核能安全委員會 (Nuclear Safety Commission)
    *   **地方政府：**
        - [ ] 臺北市政府 (Taipei City Government)
        - [ ] 新北市政府 (New Taipei City Government)
        - [ ] 桃園市政府 (Taoyuan City Government)
        - [ ] 臺中市政府 (Taichung City Government)
        - [ ] 臺南市政府 (Tainan City Government)
        - [ ] 高雄市政府 (Kaohsiung City Government)
        - [ ] 基隆市政府 (Keelung City Government)
        - [ ] 新竹市政府 (Hsinchu City Government)
        - [ ] 嘉義市政府 (Chiayi City Government)
        - [ ] 新竹縣政府 (Hsinchu County Government)
        - [ ] 苗栗縣政府 (Miaoli County Government)
        - [ ] 彰化縣政府 (Changhua County Government)
        - [ ] 南投縣政府 (Nantou County Government)
        - [ ] 雲林縣政府 (Yunlin County Government)
        - [ ] 嘉義縣政府 (Chiayi County Government)
        - [ ] 屏東縣政府 (Pingtung County Government)
        - [ ] 宜蘭縣政府 (Yilan County Government)
        - [ ] 花蓮縣政府 (Hualien County Government)
        - [ ] 臺東縣政府 (Taitung County Government)
        - [ ] 澎湖縣政府 (Penghu County Government)
        - [ ] 金門縣政府 (Kinmen County Government)
        - [ ] 連江縣政府 (Lienchiang County Government)
