import sqlite3
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
from fastapi.middleware.cors import CORSMiddleware

# --- Configuration ---
DATABASE_FILE = "gov_opendata_platform.db"
# Assuming the database file is in the same directory as main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, DATABASE_FILE)

# --- Pydantic Models ---
class OpenDataItem(BaseModel):
    id: str = Field(..., alias="資料集識別碼")
    name: str = Field(..., alias="資料集名稱")
    department: Optional[str] = Field(None, alias="提供機關")
    description: Optional[str] = Field(None, alias="資料集描述")
    url: Optional[str] = Field(None, alias="資料下載網址")
    category: Optional[str] = Field(None, alias="服務分類")
    update_date: Optional[str] = Field(None, alias="詮釋資料更新時間")
    
    # Additional fields from the schema
    data_provider_attribute: Optional[str] = Field(None, alias="資料提供屬性")
    quality_inspection: Optional[str] = Field(None, alias="品質檢測")
    file_format: Optional[str] = Field(None, alias="檔案格式")
    encoding_format: Optional[str] = Field(None, alias="編碼格式")
    dataset_listing_method: Optional[str] = Field(None, alias="資資料集上架方式") # Note: "資資料集" typo in schema
    main_fields_description: Optional[str] = Field(None, alias="主要欄位說明")
    update_frequency: Optional[str] = Field(None, alias="更新頻率")
    license_method: Optional[str] = Field(None, alias="授權方式")
    related_url: Optional[str] = Field(None, alias="相關網址")
    billing_method: Optional[str] = Field(None, alias="計費方式")
    contact_person_name: Optional[str] = Field(None, alias="提供機關聯絡人姓名")
    contact_person_phone: Optional[str] = Field(None, alias="提供機關聯絡人電話")
    listing_date: Optional[str] = Field(None, alias="上架日期")
    notes: Optional[str] = Field(None, alias="備註")
    data_volume: Optional[str] = Field(None, alias="資料量")

    class Config:
        allow_population_by_field_name = True # Allow initialization by field name or alias

class OpenDataListResponse(BaseModel):
    items: List[OpenDataItem]
    total: int

class OpenApiDeptItem(BaseModel):
    id: int
    promotion_status: Optional[str]
    platform_name: str
    department_unit: str
    is_central_unit: Optional[int]
    platform_description: Optional[str]
    website_link: Optional[str]
    openapi_spec_url: Optional[str]
    api_endpoint: Optional[str]
    auth_method: Optional[str]
    access_notes: Optional[str]
    meta_data: Optional[str]
    notes: Optional[str]

class OpenApiDeptListResponse(BaseModel):
    items: List[OpenApiDeptItem]
    total: int

# --- FastAPI App Initialization ---
app = FastAPI(
    title="政府開放資料測試平台 API",
    description="用於與 GovOpenApiAgent 進行對測的政府開放資料測試平台 API。",
    version="1.0.0",
    servers=[{"url": "http://localhost:8801", "description": "Local Development Server"}]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Database Connection Management ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

@app.on_event("startup")
async def startup_event():
    print(f"Connecting to database: {DB_PATH}")

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down application.")

# --- Helper function to convert DB row to OpenDataItem ---
def row_to_opendata_item(row: sqlite3.Row) -> OpenDataItem:
    # Create a dictionary from the row to pass to Pydantic model
    data = {key: row[key] for key in row.keys()}
    return OpenDataItem(**data)

def row_to_openapi_dept_item(row: sqlite3.Row) -> OpenApiDeptItem:
    data = {key: row[key] for key in row.keys()}
    return OpenApiDeptItem(**data)

# --- API Endpoints ---

@app.get("/opendata", response_model=OpenDataListResponse, summary="取得所有開放資料列表")
async def get_all_opendata(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort_by: Optional[str] = Query(None, description="排序欄位 (例如：name, department, update_date)"),
    order: str = Query("asc", regex="^(asc|desc)$", description="排序順序 (asc 或 desc)"),
):
    conn = get_db_connection()
    cursor = conn.cursor()

    where_clauses = []
    params = []

    # Build ORDER BY clause
    order_by_clause = ""
    if sort_by:
        # Map user-friendly sort_by to actual DB column names
        sort_column_map = {
            "id": "資料集識別碼",
            "name": "資料集名稱",
            "department": "提供機關",
            "category": "服務分類",
            "update_date": "詮釋資料更新時間",
            "listing_date": "上架日期"
        }
        db_sort_by = sort_column_map.get(sort_by)
        if not db_sort_by:
            raise HTTPException(status_code=400, detail=f"Invalid sort_by column: {sort_by}. Allowed: {', '.join(sort_column_map.keys())}")
        order_by_clause = f"ORDER BY \"{db_sort_by}\" {order.upper()}"

    # Get total count
    count_query = "SELECT COUNT(*) FROM open_data_catalog"
    if where_clauses:
        count_query += " WHERE " + " AND ".join(where_clauses)
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    # Get items with limit and offset
    query_sql = f"SELECT * FROM open_data_catalog {order_by_clause} LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    cursor.execute(query_sql, params)
    items = [row_to_opendata_item(row) for row in cursor.fetchall()]

    conn.close()
    return OpenDataListResponse(items=items, total=total)

@app.get("/opendata/search", response_model=OpenDataListResponse, summary="搜尋開放資料")
async def search_opendata(
    query: str = Query(..., min_length=1, description="搜尋關鍵字，可匹配資料集名稱、資料集描述、提供機關等"),
    department: Optional[str] = Query(None, description="依提供機關名稱篩選"),
    category: Optional[str] = Query(None, description="依服務分類篩選"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort_by: Optional[str] = Query(None, description="排序欄位 (例如：name, department, update_date)"),
    order: str = Query("asc", regex="^(asc|desc)$", description="排序順序 (asc 或 desc)"),
):
    conn = get_db_connection()
    cursor = conn.cursor()

    where_clauses = []
    params = []

    # General query
    search_pattern = f"%{query}%"
    where_clauses.append("(\"資料集名稱\" LIKE ? OR \"資料集描述\" LIKE ? OR \"提供機關\" LIKE ?)")
    params.extend([search_pattern, search_pattern, search_pattern])

    if department:
        where_clauses.append("\"提供機關\" = ?")
        params.append(department)
    if category:
        where_clauses.append("\"服務分類\" = ?")
        params.append(category)

    # Build ORDER BY clause
    order_by_clause = ""
    if sort_by:
        sort_column_map = {
            "id": "資料集識別碼",
            "name": "資料集名稱",
            "department": "提供機關",
            "category": "服務分類",
            "update_date": "詮釋資料更新時間",
            "listing_date": "上架日期"
        }
        db_sort_by = sort_column_map.get(sort_by)
        if not db_sort_by:
            raise HTTPException(status_code=400, detail=f"Invalid sort_by column: {sort_by}. Allowed: {', '.join(sort_column_map.keys())}")
        order_by_clause = f"ORDER BY \"{db_sort_by}\" {order.upper()}"

    # Get total count
    count_query = "SELECT COUNT(*) FROM open_data_catalog"
    if where_clauses:
        count_query += " WHERE " + " AND ".join(where_clauses)
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    # Get items with limit and offset
    query_sql = f"SELECT * FROM open_data_catalog"
    if where_clauses:
        query_sql += " WHERE " + " AND ".join(where_clauses)
    query_sql += f" {order_by_clause} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query_sql, params)
    items = [row_to_opendata_item(row) for row in cursor.fetchall()]

    conn.close()
    return OpenDataListResponse(items=items, total=total)


@app.get("/opendata/categories", response_model=List[str], summary="取得開放資料類別列表")
async def get_opendata_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT \"服務分類\" FROM open_data_catalog WHERE \"服務分類\" IS NOT NULL AND \"服務分類\" != '' ORDER BY \"服務分類\"")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

@app.get("/opendata/departments", response_model=List[str], summary="取得開放資料提供單位列表")
async def get_opendata_departments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT \"提供機關\" FROM open_data_catalog WHERE \"提供機關\" IS NOT NULL AND \"提供機關\" != '' ORDER BY \"提供機關\"")
    departments = [row[0] for row in cursor.fetchall()]
    conn.close()
    return departments

@app.get("/opendata/{item_id}", response_model=OpenDataItem, summary="取得單一開放資料詳情")
async def get_opendata_item(item_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM open_data_catalog WHERE \"資料集識別碼\" = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Open data item not found")
    return row_to_opendata_item(row)

@app.get("/openapi_depts", response_model=OpenApiDeptListResponse, summary="取得所有 OpenAPI 部門資料列表")
async def get_all_openapi_depts(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort_by: Optional[str] = Query(None, description="排序欄位 (例如：platform_name, department_unit)"),
    order: str = Query("asc", regex="^(asc|desc)$", description="排序順序 (asc 或 desc)"),
):
    conn = get_db_connection()
    cursor = conn.cursor()

    where_clauses = []
    params = []

    order_by_clause = ""
    if sort_by:
        sort_column_map = {
            "id": "id",
            "promotion_status": "promotion_status",
            "platform_name": "platform_name",
            "department_unit": "department_unit",
            "is_central_unit": "is_central_unit",
            "website_link": "website_link"
        }
        db_sort_by = sort_column_map.get(sort_by)
        if not db_sort_by:
            raise HTTPException(status_code=400, detail=f"Invalid sort_by column: {sort_by}. Allowed: {', '.join(sort_column_map.keys())}")
        order_by_clause = f"ORDER BY \"{db_sort_by}\" {order.upper()}"

    count_query = "SELECT COUNT(*) FROM openapi_dept"
    if where_clauses:
        count_query += " WHERE " + " AND ".join(where_clauses)
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    query_sql = f"SELECT * FROM openapi_dept {order_by_clause} LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    cursor.execute(query_sql, params)
    items = [row_to_openapi_dept_item(row) for row in cursor.fetchall()]

    conn.close()
    return OpenApiDeptListResponse(items=items, total=total)

@app.get("/openapi_depts/{dept_id}", response_model=OpenApiDeptItem, summary="取得單一 OpenAPI 部門詳情")
async def get_openapi_dept_item(dept_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM openapi_dept WHERE id = ?", (dept_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="OpenAPI department item not found")
    return row_to_openapi_dept_item(row)

# To run the server:
# uvicorn gov_opendata_platform:app --reload --port 8801  