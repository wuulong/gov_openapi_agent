import os
import sys
import json
import yaml
from collections import defaultdict

def load_openapi_spec(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        if filepath.endswith(('.yaml', '.yml')):
            return yaml.safe_load(f)
        elif filepath.endswith('.json'):
            return json.load(f)
        else:
            raise ValueError("Unsupported file format")

def save_openapi_spec(filepath: str, spec):
    with open(filepath, 'w', encoding='utf-8') as f:
        if filepath.endswith(('.yaml', '.yml')):
            yaml.safe_dump(spec, f, allow_unicode=True, sort_keys=False)
        elif filepath.endswith('.json'):
            json.dump(spec, f, ensure_ascii=False, indent=2)

def fix_duplicate_operation_ids_in_file(filepath: str):
    if not os.path.exists(filepath):
        print(f"錯誤: 檔案 '{filepath}' 不存在。")
        return

    print(f"開始檢查並修復檔案 '{filepath}' 中的 OpenAPI 規範...")
    
    try:
        spec = load_openapi_spec(filepath)
        if 'paths' not in spec:
            print(f"  警告: 檔案 {os.path.basename(filepath)} 沒有 'paths' 區塊，跳過。")
            return

        operation_ids = defaultdict(list)
        
        # 收集所有 operationId
        for path, methods in spec['paths'].items():
            for method, operation_info in methods.items():
                if 'operationId' in operation_info:
                    operation_ids[operation_info['operationId']].append((path, method))

        # 找出重複的 operationId 並修復
        modified = False
        for op_id, locations in operation_ids.items():
            if len(locations) > 1:
                print(f"  發現重複的 operationId: '{op_id}'，位於:")
                for path, method in locations:
                    print(f"    - 路徑: '{path}', 方法: '{method}'")
                
                # 修復重複的 operationId
                for i, (path, method) in enumerate(locations):
                    # 生成新的唯一 ID，結合原始 op_id, 路徑和方法
                    # 將路徑中的特殊字元替換掉，使其適合作為 operationId 的一部分
                    clean_path = path.replace('/', '_').replace('{', '').replace('}', '')
                    new_op_id = f"{op_id}_{clean_path}_{method}"
                    # 確保新的 operationId 不會太長或包含不允許的字元
                    # 這裡只做簡單替換，更嚴格的檢查可能需要正則表達式
                    new_op_id = new_op_id.replace('__', '_').strip('_')

                    spec['paths'][path][method]['operationId'] = new_op_id
                    print(f"    - 將 '{path}' 的 '{method}' 方法的 operationId 修改為: '{new_op_id}'")
                    modified = True
        
        if modified:
            save_openapi_spec(filepath, spec)
            print(f"  檔案 {os.path.basename(filepath)} 已修復並保存。")
        else:
            print(f"  檔案 {os.path.basename(filepath)} 沒有重複的 operationId，無需修改。")

    except Exception as e:
        print(f"  ❌ 處理檔案 {os.path.basename(filepath)} 時發生錯誤: {e}")

    print("\n檔案處理完畢。")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fix_openapi_operation_ids.py <要檢查的檔案路徑>")
        print("範例: python fix_openapi_operation_ids.py config/openapi_specs/your_spec.json")
    else:
        target_file = sys.argv[1]
        fix_duplicate_operation_ids_in_file(target_file)
