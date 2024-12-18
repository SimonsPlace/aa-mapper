import re
import os

def parse_api_calls(project_path):
    """
    Parses API calls from JavaScript/TypeScript files.
    Supports Fetch, Axios, and other common patterns.
    """
    api_calls = []

    # Patterns to match different types of API calls
    fetch_pattern = r'fetch\((["\'])(.*?)\1.*?method:\s*(["\'])(GET|POST|PUT|DELETE|PATCH)\3'
    axios_pattern = r'axios\.(get|post|put|delete|patch)\((["\'])(.*?)\2'
    custom_http_pattern = r'\w+\.(get|post|put|delete|patch)\((["\'])(.*?)\2'

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(('.js', '.ts', '.jsx', '.tsx')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                        # Match Fetch API
                        for match in re.finditer(fetch_pattern, content, re.DOTALL):
                            api_calls.append({
                                "endpoint": match.group(2),
                                "method": match.group(4),
                                "request_body": None
                            })

                        # Match Axios calls
                        for match in re.finditer(axios_pattern, content):
                            api_calls.append({
                                "endpoint": match.group(3),
                                "method": match.group(1).upper(),
                                "request_body": None
                            })

                        # Match Custom HTTP Clients
                        for match in re.finditer(custom_http_pattern, content):
                            api_calls.append({
                                "endpoint": match.group(3),
                                "method": match.group(1).upper(),
                                "request_body": None
                            })

                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    print(f"Total API calls parsed: {len(api_calls)}")
    return api_calls
