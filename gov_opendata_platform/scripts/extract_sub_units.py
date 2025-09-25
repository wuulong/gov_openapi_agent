import re
import sys

def extract_first_level_sub_units(file_path, target_unit_name):
    """
    從政府組織架構文件中提取指定單位的第一級子單位。

    Args:
        file_path (str): 政府組織架構文件的路徑。
        target_unit_name (str): 要查找的目標單位名稱 (例如 "經濟部")。

    Returns:
        list: 包含第一級子單位名稱的列表。
    """
    sub_units = []
    target_indent_level = -1
    found_target = False

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            stripped_line = line.rstrip() # Use rstrip to keep leading spaces for indent calculation
            if not stripped_line:
                continue

            # Calculate current indentation level
            # A level is defined by the number of '|   ' prefixes
            # The actual unit name starts after '|-- ' or '+-- '
            match = re.match(r'^(?:\|   )*(?:\|--|\+--)\s*(.*)', stripped_line)
            if not match:
                continue

            current_indent_prefix = re.match(r'^(?:\|   )*', stripped_line)
            current_indent_level = len(current_indent_prefix.group(0)) // 4 if current_indent_prefix else 0

            unit_in_line = match.group(1).strip()

            if target_unit_name in unit_in_line and not found_target:
                found_target = True
                target_indent_level = current_indent_level
                continue

            if found_target:
                if current_indent_level == target_indent_level + 1:
                    # This is a direct sub-unit
                    sub_units.append(unit_in_line)
                elif current_indent_level <= target_indent_level:
                    # We have moved out of the target unit's hierarchy
                    break
    return sub_units

if __name__ == "__main__":
    # 檔案路徑
    file_path = '/Volumes/D2024/github/gov_openapi_agent/data/政府組織架構_全.txt'

    # 從命令列參數獲取目標單位名稱
    if len(sys.argv) > 1:
        target_unit = sys.argv[1]
    else:
        print("請指定要查詢的目標單位名稱。例如: python extract_sub_units.py 經濟部")
        sys.exit(1)

    # 執行提取
    economic_affairs_sub_units = extract_first_level_sub_units(file_path, target_unit)

    # 打印結果
    print(f"{target_unit} 下面的第一級子單位清單:")
    if economic_affairs_sub_units:
        for unit in economic_affairs_sub_units:
            print(f"- {unit}")
    else:
        print(f"找不到 {target_unit} 或其第一級子單位。")