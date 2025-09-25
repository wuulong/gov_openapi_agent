import json
import os
import argparse # Import argparse

def fix_openapi_security(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        swagger_spec = json.load(f)

    # 1. Add securityDefinitions if not already present
    if "securityDefinitions" not in swagger_spec:
        swagger_spec["securityDefinitions"] = {}
    
    if "ApiKeyAuth" not in swagger_spec["securityDefinitions"]:
        swagger_spec["securityDefinitions"]["ApiKeyAuth"] = {
            "type": "apiKey",
            "in": "query",
            "name": "Authorization"
        }

    # 2. Iterate through paths and operations to modify them
    if "paths" in swagger_spec:
        for path, methods in swagger_spec["paths"].items():
            for method, operation in methods.items():
                # Store original parameters to check if Authorization was present
                original_parameters = operation.get("parameters", [])
                
                # Filter out the old Authorization parameter
                new_parameters = [
                    p for p in original_parameters
                    if not (p.get("name") == "Authorization" and p.get("in") == "query")
                ]
                operation["parameters"] = new_parameters
                
                # Add the security reference if not already present and if it was an authenticated endpoint
                # We assume if it had an Authorization parameter, it needs security.
                if any(p.get("name") == "Authorization" and p.get("in") == "query" for p in original_parameters):
                    if "security" not in operation:
                        operation["security"] = [{"ApiKeyAuth": []}]
                    elif {"ApiKeyAuth": []} not in operation["security"]:
                        operation["security"].append({"ApiKeyAuth": []})


    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(swagger_spec, f, indent=2, ensure_ascii=False)

    print(f"Successfully updated {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix OpenAPI security definitions in a Swagger/OpenAPI JSON file.")
    parser.add_argument("file_path", help="The absolute path to the Swagger/OpenAPI JSON file.")
    args = parser.parse_args()

    if os.path.exists(args.file_path):
        fix_openapi_security(args.file_path)
    else:
        print(f"Error: {args.file_path} not found.")