# src/parser/platform_analyzer.py
import os
import re
import logging

def analyze_platform_specific_code(project_path):
    """
    Scans the project to detect platform-specific code and iOS-only dependencies, suggesting Android alternatives.
    """

    platform_issues = []

    # Patterns for platform-specific checks and iOS-only dependencies
    platform_os_pattern = r"Platform\.OS\s*===\s*['\"]ios['\"]"
    ios_library_pattern = re.compile(r"import\s+.*?from\s+['\"](.*?)['\"]")

    # Known iOS-only libraries to flag
    ios_only_libraries = [
        "react-native-push-notification-ios",
        "@react-native-community/push-notification-ios",
        "react-native-permissions/ios",
        "react-native-navigation/ios",
        "some-custom-ios-module"
    ]

    # Mapping from iOS-only libraries to recommended Android equivalents
    ios_to_android_equivalents = {
        "@react-native-community/push-notification-ios": ("react-native-push-notification", "https://github.com/zo0r/react-native-push-notification"),
        "react-native-push-notification-ios": ("react-native-push-notification", "https://github.com/zo0r/react-native-push-notification"),
        "react-native-permissions/ios": ("react-native-permissions (with Android setup)", "https://github.com/zo0r/react-native-push-notification"),
        # Add more mappings as needed
    }

    logging.info("Starting platform-specific code analysis...")

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".js") or file.endswith(".tsx"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                except Exception as e:
                    logging.error(f"Error reading file {file_path}: {e}")
                    continue

                # Search for platform-specific code
                for line_num, line in enumerate(lines, start=1):
                    if re.search(platform_os_pattern, line):
                        platform_issues.append({
                            "file_path": file_path,
                            "line_number": line_num,
                            "issue_type": "platform_code",
                            "details": line.strip()
                            # No docs_link or recommendation here, but you can add if needed
                        })

                    # Search for iOS-only libraries
                    match = ios_library_pattern.search(line)
                    if match:
                        imported_library = match.group(1)
                        if any(ios_lib in imported_library for ios_lib in ios_only_libraries):
                            suggestion_details = imported_library + " (iOS-only)."
                            docs_link = ""
                            recommendation = ""

                            for ios_lib in ios_only_libraries:
                                if ios_lib in imported_library:
                                    if ios_lib in ios_to_android_equivalents:
                                        android_lib, doc_link = ios_to_android_equivalents[ios_lib]
                                        suggestion_details += f" Consider using '{android_lib}' for Android. Docs: {doc_link}"
                                        docs_link = doc_link
                                        recommendation = f"Replace {ios_lib} with {android_lib} for Android compatibility."
                                    else:
                                        suggestion_details += " No known Android equivalent found. Check community resources or official docs."
                                    break

                            platform_issues.append({
                                "file_path": file_path,
                                "line_number": line_num,
                                "issue_type": "ios_library",
                                "details": suggestion_details,
                                "docs_link": docs_link,
                                "recommendation": recommendation
                            })

    logging.info("Platform-specific analysis complete.")
    return platform_issues
