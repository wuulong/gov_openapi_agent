import os
import sys
import yaml
from openapi_spec_validator import validate_spec
from jsonschema.exceptions import ValidationError

def validate_openapi_spec_file(filepath: str) -> bool:
    """
    驗證單個 OpenAPI YAML 規範檔案。
    如果有效則返回 True，否則返回 False 並印出錯誤。
    """
    print(f"正在檢查檔案: {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            spec = yaml.safe_load(f)
        
        # 嘗試驗證 OpenAPI 3.0 規範
        validate_spec(spec)
        print(f"  ✅ {filepath} 驗證成功！")
        return True
    except FileNotFoundError:
        print(f"  ❌ 錯誤: 檔案未找到 - {filepath}")
        return False
    except yaml.YAMLError as e:
        print(f"  ❌ 錯誤: YAML 解析錯誤 - {filepath}: {e}")
        return False
    except ValidationError as e:
        print(f"  ❌ 錯誤: OpenAPI 驗證失敗 - {filepath}:")
        print(f"    {e}")
        return False
    except Exception as e:
        print(f"  ❌ 發生未知錯誤 - {filepath}: {e}")
        return False

def validate_openapi_specs_in_directory(directory_path: str):
    """
    驗證指定目錄中所有 .yaml 和 .yml 檔案。
    """
    if not os.path.isdir(directory_path):
        print(f"錯誤: 目錄 '{directory_path}' 不存在。")
        return

    print(f"開始驗證目錄 '{directory_path}' 中的 OpenAPI 規範檔案...")
    all_valid = True
    for filename in os.listdir(directory_path):
        if filename.endswith((".yaml", ".yml",".json")):
            filepath = os.path.join(directory_path, filename)
            if not validate_openapi_spec_file(filepath):
                all_valid = False
    
    if all_valid:
        print("\n所有檔案都已成功驗證！")
    else:
        print("\n部分檔案驗證失敗，請檢查上述錯誤訊息。" )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python validate_openapi.py <要檢查的目錄路徑>")
        print("範例: python validate_openapi.py my_samples/moenv_openapi_agent/")
    else:
        target_directory = sys.argv[1]
        validate_openapi_specs_in_directory(target_directory)
