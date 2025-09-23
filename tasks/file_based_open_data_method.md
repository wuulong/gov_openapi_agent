
處理檔案型開放資料並回答使用者問題的方法步驟如下：

1.  **理解使用者需求並識別資料集**：
    *   仔細閱讀使用者的問題，判斷他們需要哪種類型的開放資料。
    *   使用 `process_user_prompt` 函數，以自然語言查詢相關資料集，例如：「/openapi-agent [關鍵字] 相關資料」。
    *   從 `process_user_prompt` 的回覆中，識別出最符合使用者需求的資料集名稱和描述。

2.  **取得資料集的下載點**：
    *   一旦識別出資料集，再次使用 `process_user_prompt` 函數，詢問該資料集的下載點，例如：「[資料集名稱] 的 [檔案格式] 下載點」。
    *   從回覆中獲取所需的檔案格式（例如 CSV, JSON, XML, ZIP 等）的下載 URL。

3.  **下載資料檔案**：
    *   如果 `web_fetch` 工具因故無法使用，則使用 `run_shell_command` 搭配 `wget` 指令來下載檔案。
    *   為了避免被網站阻擋，建議在 `wget` 指令中加入 `--user-agent` 參數，模擬瀏覽器行為。
    *   先使用 `mkdir -p tmp` 建立一個暫存資料夾（如果不存在），然後將檔案下載到該資料夾，例如：
        ```bash
        mkdir -p tmp
        wget --user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36" -O tmp/[檔案名稱].[副檔名] '[下載URL]'
        ```
    *   **處理壓縮檔案 (例如 Shapefile)**: 如果下載的是壓縮檔案 (例如 `.zip`)，需要使用 `unzip` 指令解壓縮到一個新的子資料夾中，例如：
        ```bash
        mkdir -p tmp/data_folder
        unzip tmp/[壓縮檔案名稱].zip -d tmp/data_folder
        ```
    *   確保下載成功，檢查 `run_shell_command` 的輸出。

4.  **讀取並解析下載的檔案**：
    *   使用 `read_file` 工具讀取下載到暫存資料夾的檔案內容，例如：
        ```python
        read_file(absolute_path = "/Volumes/D2024/github/gov_openapi_agent/tmp/[檔案名稱].[副檔名]")
        ```
    *   根據檔案格式（例如 CSV, JSON），解析檔案內容。對於 CSV 檔案，需要識別標頭行和資料行，並根據列名提取所需資訊。
    *   **處理地理空間資料 (例如 Shapefile)**:
        *   Shapefile 通常包含多個檔案 (例如 `.shp`, `.shx`, `.dbf`, `.prj`)，需要完整解壓縮後才能讀取。
        *   可以使用 `fiona` 程式庫或其命令列工具 `fio` 來檢查和解析 Shapefile。
        *   使用 `fio info [shp檔案路徑]` 可以查看 Shapefile 的元資料 (例如座標系統、幾何類型、屬性欄位)。
        *   使用 `fio dump [shp檔案路徑] > [輸出檔案.json]` 可以將 Shapefile 的特徵資料導出為 GeoJSON 格式，方便進一步處理。

5.  **從資料中提取答案並回覆使用者**：
    *   根據使用者的原始問題，從解析後的資料中找出相關的資訊。
    *   如果資料中沒有直接的名稱對應，但有相關的識別碼，則需要根據上下文進行推斷，並在回覆中說明推斷的依據。
    *   對於 GeoJSON 格式的資料，可以使用 `jq` 等工具進行查詢和提取特定屬性。
    *   將提取到的答案以清晰簡潔的方式回覆給使用者。