import os
import sys
import json
import yaml
import re
from collections import defaultdict

def load_openapi_spec(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        if filepath.endswith(('.yaml', '.yml')):
            return yaml.safe_load(content)
        elif filepath.endswith('.json'):
            # 嘗試修復單引號鍵名為雙引號鍵名
            # 這裡只處理簡單的鍵名，避免誤傷字串值中的單引號
            content = re.sub(r"'([a-zA-Z_][a-zA-Z0-9_]*)':", r'"\1":', content)
            # 嘗試修復布林值
            content = content.replace(': True', ': true').replace(': False', ': false')
            return json.loads(content)
        else:
            raise ValueError("Unsupported file format")

def save_openapi_spec(filepath: str, spec):
    with open(filepath, 'w', encoding='utf-8') as f:
        if filepath.endswith(('.yaml', '.yml')):
            yaml.safe_dump(spec, f, allow_unicode=True, sort_keys=False)
        elif filepath.endswith('.json'):
            json.dump(spec, f, ensure_ascii=False, indent=2)

def fix_default_type_in_parameters(parameters):
    modified = False
    if parameters:
        for param in parameters:
            if 'default' in param and 'type' in param:
                default_value = param['default']
                param_type = param['type']

                if isinstance(default_value, str):
                    if param_type == 'integer':
                        try:
                            param['default'] = int(default_value)
                            print(f"    - 將參數 '{param.get('name', '未知')}' 的 default 值從字串 '{default_value}' 轉換為整數 {param['default']}")
                            modified = True
                        except ValueError:
                            pass # 無法轉換為整數，保持原樣
                    elif param_type == 'number':
                        try:
                            param['default'] = float(default_value)
                            print(f"    - 將參數 '{param.get('name', '未知')}' 的 default 值從字串 '{default_value}' 轉換為數字 {param['default']}")
                            modified = True
                        except ValueError:
                            pass # 無法轉換為數字，保持原樣
    return modified

def add_missing_description_to_schema(obj):
    modified = False
    if isinstance(obj, dict):
        # 檢查當前字典是否為 schema 或包含 schema
        if 'schema' in obj and isinstance(obj['schema'], dict):
            if 'description' not in obj['schema']:
                obj['schema']['description'] = ""
                modified = True
                print(f"    - 為 schema 添加空的 description 屬性")
                # print(f"    - 缺少 description 的 schema 內容: {json.dumps(obj['schema'], ensure_ascii=False, indent=2)}") # 調試輸出
            # 遞歸檢查 schema 內部，特別是 items
            if add_missing_description_to_schema(obj['schema']):
                modified = True
        
        # 檢查 items 屬性，通常用於 array 類型
        if 'items' in obj and isinstance(obj['items'], dict):
            if 'description' not in obj['items']:
                obj['items']['description'] = ""
                modified = True
                print(f"    - 為 items schema 添加空的 description 屬性")
                # print(f"    - 缺少 description 的 items schema 內容: {json.dumps(obj['items'], ensure_ascii=False, indent=2)}") # 調試輸出
            # 遞歸檢查 items 內部
            if add_missing_description_to_schema(obj['items']):
                modified = True

        # 遞歸檢查所有字典值
        for key, value in obj.items():
            if key not in ['schema', 'items'] and add_missing_description_to_schema(value):
                modified = True
    elif isinstance(obj, list):
        # 遞歸檢查列表中的每個元素
        for item in obj:
            if add_missing_description_to_schema(item):
                modified = True
    return modified

def fix_openapi_default_types_in_file(filepath: str):
    if not os.path.exists(filepath):
        print(f"錯誤: 檔案 '{filepath}' 不存在。")
        return

    print(f"開始檢查並修復檔案 '{filepath}' 中的 OpenAPI 規範 default 類型錯誤和缺少 description 屬性問題...")
    
    try:
        spec = load_openapi_spec(filepath)
        file_modified = False

        if 'paths' in spec:
            for path, methods in spec['paths'].items():
                for method, operation_info in methods.items():
                    if 'parameters' in operation_info:
                        print(f"  檢查路徑 '{path}' 方法 '{method}' 的參數...")
                        if fix_default_type_in_parameters(operation_info['parameters']):
                            file_modified = True
                        # 檢查參數中的 schema 是否缺少 description
                        for param in operation_info['parameters']:
                            # 這裡直接檢查 param 本身是否缺少 description，因為 operation_parser.py 嘗試訪問的是 param.description
                            if 'description' not in param:
                                param['description'] = ""
                                file_modified = True
                                print(f"    - 為參數 '{param.get('name', '未知')}' 添加空的 description 屬性")
                            
                            # 檢查 param.schema 是否缺少 description
                            if 'schema' in param and isinstance(param['schema'], dict):
                                if 'description' not in param['schema']:
                                    param['schema']['description'] = ""
                                    file_modified = True
                                    print(f"    - 為參數 '{param.get('name', '未知')}' 的 schema 添加空的 description 屬性")

                            if add_missing_description_to_schema(param):
                                file_modified = True

                    if 'responses' in operation_info:
                        # 檢查 responses 中的 schema 是否缺少 description
                        for status_code, response_info in operation_info['responses'].items():
                            if add_missing_description_to_schema(response_info):
                                file_modified = True

        # 檢查 components/parameters (OpenAPI 3.0) 或 definitions (Swagger 2.0) 中的參數
        if 'components' in spec and 'parameters' in spec['components']:
            print("  檢查 components/parameters 中的參數...")
            for param_name, param_info in spec['components']['parameters'].items():
                if 'default' in param_info and 'type' in param_info:
                    default_value = param_info['default']
                    param_type = param_info['type']
                    if isinstance(default_value, str):
                        if param_type == 'integer':
                            try:
                                spec['components']['parameters'][param_name]['default'] = int(default_value)
                                print(f"    - 將 components/parameters 中 '{param_name}' 的 default 值從字串 '{default_value}' 轉換為整數 {spec['components']['parameters'][param_name]['default']}")
                                file_modified = True
                            except ValueError:
                                pass
                        elif param_type == 'number':
                            try:
                                spec['components']['parameters'][param_name]['default'] = float(default_value)
                                print(f"    - 將 components/parameters 中 '{param_name}' 的 default 值從字串 '{default_value}' 轉換為數字 {spec['components']['parameters'][param_name]['default']}")
                                file_modified = True
                            except ValueError:
                                pass
                if add_missing_description_to_schema(param_info):
                    file_modified = True
        
        # 針對 Swagger 2.0 的 definitions 處理
        if 'definitions' in spec:
            for def_name, def_info in spec['definitions'].items():
                if 'properties' in def_info:
                    for prop_name, prop_info in def_info['properties'].items():
                        if 'default' in prop_info and 'type' in prop_info:
                            default_value = prop_info['default']
                            prop_type = prop_info['type']
                            if isinstance(default_value, str):
                                if prop_type == 'integer':
                                    try:
                                        spec['definitions'][def_name]['properties'][prop_name]['default'] = int(default_value)
                                        print(f"    - 將 definition '{def_name}' 屬性 '{prop_name}' 的 default 值從字串 '{default_value}' 轉換為整數 {spec['definitions'][def_name]['properties'][prop_name]['default']}")
                                        file_modified = True
                                    except ValueError:
                                        pass
                                elif prop_type == 'number':
                                    try:
                                        spec['definitions'][def_name]['properties'][prop_name]['default'] = float(default_value)
                                        print(f"    - 將 definition '{def_name}' 屬性 '{prop_name}' 的 default 值從字串 '{default_value}' 轉換為數字 {spec['definitions'][def_name]['properties'][prop_name]['default']}")
                                        file_modified = True
                                    except ValueError:
                                        pass
                if add_missing_description_to_schema(def_info):
                    file_modified = True

        if file_modified:
            save_openapi_spec(filepath, spec)
            print(f"  檔案 {os.path.basename(filepath)} 已修復並保存。")
        else:
            print(f"  檔案 {os.path.basename(filepath)} 沒有 default 類型錯誤或缺少 description 屬性，無需修改。")

    except Exception as e:
        print(f"  ❌ 處理檔案 {os.path.basename(filepath)} 時發生錯誤: {e}")

    print("\n檔案處理完畢。")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fix_openapi_default_types.py <要檢查的檔案路徑>\
               或 python fix_openapi_default_types.py <要檢查的目錄路徑>")
        print("範例: python fix_openapi_default_types.py config/openapi_specs/your_spec.json")
        print("範例: python fix_openapi_default_types.py config/openapi_specs/")
    else:
        target_path = sys.argv[1]
        if os.path.isdir(target_path):
            for filename in os.listdir(target_path):
                if filename.endswith(('.yaml', '.yml', '.json')):
                    filepath = os.path.join(target_path, filename)
                    fix_openapi_default_types_in_file(filepath)
        elif os.path.isfile(target_path):
            fix_openapi_default_types_in_file(target_path)
        else:
            print(f"錯誤: '{target_path}' 不是有效的檔案或目錄路徑。")