import os
import yaml
import json
import argparse

def fix_openapi_response_keys(file_path):
    """
    Fixes OpenAPI specification files by converting integer response keys (e.g., 200)
    to string keys (e.g., "200") in the 'responses' object.
    """
    print(f"Processing file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to load as YAML first, then JSON
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError:
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                print(f"Error: Could not parse {file_path} as YAML or JSON. Skipping.")
                return

        changed = False
        if isinstance(data, dict) and 'paths' in data:
            for path, methods in data['paths'].items():
                if isinstance(methods, dict):
                    for method, details in methods.items():
                        if isinstance(details, dict) and 'responses' in details:
                            responses = details['responses']
                            new_responses = {}
                            for key, value in responses.items():
                                if isinstance(key, int):
                                    new_responses[str(key)] = value
                                    changed = True
                                else:
                                    new_responses[key] = value
                            details['responses'] = new_responses
        
        if changed:
            print(f"Changes detected in {file_path}. Saving...")
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith(('.yaml', '.yml')):
                    yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                else:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Successfully fixed and saved {file_path}")
        else:
            print(f"No changes needed for {file_path}")

    except Exception as e:
        print(f"An error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix OpenAPI response keys in a single file.")
    parser.add_argument("file_path", help="The path to the OpenAPI specification file.")
    args = parser.parse_args()

    fix_openapi_response_keys(args.file_path)