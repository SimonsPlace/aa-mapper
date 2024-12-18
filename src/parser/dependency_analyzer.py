import os
import re

def parse_dependencies(project_path):
    """
    Parses React Native project files for dependencies.
    """
    dependencies = []

    import_pattern = re.compile(r"import .*? from ['\"](.*?)['\"]")

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".js") or file.endswith(".tsx"):
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        match = import_pattern.match(line)
                        if match:
                            dependencies.append({
                                "source": file_path,          # Source file path
                                "target": match.group(1),    # Imported module/file
                                "type": "import",            # Type of dependency
                                "file_path": file_path       # File path for traceability
                            })

    return dependencies
