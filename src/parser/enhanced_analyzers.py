import os
import re

def analyze_ui_patterns(project_path):
    """
    Scans the codebase for iOS-specific UI patterns and suggests Android equivalents.
    Patterns:
      - TabBarIOS -> suggest BottomNavigationView
      - NavigationController -> suggest NavigationDrawer (or React Navigation)
      - <Modal -> suggest DialogFragment or AlertDialog
    """

    patterns = [
        {
            "ios_pattern": "TabBarIOS",
            "pattern_type": "TabBar",
            "suggested_android": "BottomNavigationView",
            "regex": re.compile(r'\bTabBarIOS\b')
        },
        {
            "ios_pattern": "NavigationController",
            "pattern_type": "NavigationController",
            "suggested_android": "NavigationDrawer (React Navigation)",
            "regex": re.compile(r'\bNavigationController\b')
        },
        {
            "ios_pattern": "<Modal",
            "pattern_type": "Modal",
            "suggested_android": "DialogFragment/AlertDialog",
            "regex": re.compile(r'<Modal\b', re.IGNORECASE)
        }
    ]

    ui_issues = []

    # Walk through the project files
    for root, _, files in os.walk(project_path):
        for file in files:
            # Consider JS and TSX files as React Native code files
            if file.endswith(".js") or file.endswith(".tsx"):
                file_path = os.path.join(root, file)
                screen_name = os.path.splitext(file)[0]

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    # Check each pattern
                    for line_num, line in enumerate(lines, start=1):
                        for pat in patterns:
                            if pat["regex"].search(line):
                                # Found a pattern
                                ui_issues.append({
                                    "screen_name": screen_name,
                                    "pattern_type": pat["pattern_type"],
                                    "suggested_android": pat["suggested_android"],
                                    "details": f"Found {pat['ios_pattern']} at {file_path}:{line_num}"
                                })
                except Exception as e:
                    # If there's a file reading error, just skip that file
                    pass

    return ui_issues

def analyze_device_styling(project_path):
    """
    Finds hardcoded px values or iOS-specific styling references and suggests Android-friendly approaches.
    Heuristics:
      - Detect `height:` or `width:` with numeric values in styles.
      - Detect `Platform.OS === 'ios'` in styling logic and suggest Material Components for Android.
      - Provide a link to Material Design guidelines.
    """

    styling_issues = []
    # Regex to find style assignments like `height: 100,` or `margin: 24`
    # This is simplistic and may have false positives.
    numeric_style_pattern = re.compile(r'\b(height|width|margin|padding|top|left|right|bottom)\s*:\s*(\d+)\b')

    # Detect iOS checks in styling logic
    ios_check_pattern = re.compile(r'Platform\.OS\s*===\s*[\'"]ios[\'"]')

    # Material design docs:
    material_docs = "https://material.io/design"

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".js") or file.endswith(".tsx"):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    for line_num, line in enumerate(lines, start=1):
                        # Check for numeric styles
                        for match in numeric_style_pattern.finditer(line):
                            prop, value = match.groups()
                            # Suggest using dp or a responsive scaling library
                            styling_issues.append({
                                "file_path": file_path,
                                "line_number": line_num,
                                "issue_type": "hardcoded_style",
                                "details": f"Found {prop}: {value}px. Consider using dp units or responsive scaling for Android.",
                                "recommendation": "Use scalable units (e.g., Dimensions API or react-native-size-matters) for responsive design.",
                                "docs_link": "https://reactnative.dev/docs/platform-specific-code#dimensions"
                            })

                        # Check for iOS-specific conditions in styling
                        if ios_check_pattern.search(line):
                            styling_issues.append({
                                "file_path": file_path,
                                "line_number": line_num,
                                "issue_type": "ios_specific_styling",
                                "details": "Detected iOS-only styling condition.",
                                "recommendation": "Use platform-agnostic Material Design components or conditional platform checks with equivalent Android design.",
                                "docs_link": material_docs
                            })

                except Exception:
                    # Skip unreadable files
                    pass

    return styling_issues

def analyze_api_behavior(project_path):
    """
    Identifies common APIs that behave differently on Android and offers recommendations.

    Heuristics:
      - PushNotificationIOS -> Suggest react-native-push-notification
      - Geolocation -> Mention adding Android location permissions
      - CameraRoll -> Mention storage permissions for Android
      - react-native-fs (FileSystem) -> Mention WRITE_EXTERNAL_STORAGE permission on Android
    """

    api_issues = []

    # Patterns and guidance
    patterns = [
        {
            "regex": re.compile(r'\bPushNotificationIOS\b'),
            "api_name": "PushNotificationIOS",
            "ios_usage": "Used for iOS push notifications.",
            "android_considerations": "Use react-native-push-notification for Android and ensure FCM or a similar service is integrated.",
            "docs_link": "https://github.com/zo0r/react-native-push-notification"
        },
        {
            "regex": re.compile(r'\bGeolocation\.getCurrentPosition\b|\bnavigator\.geolocation\b'),
            "api_name": "Geolocation",
            "ios_usage": "Used for location on iOS.",
            "android_considerations": "Add ACCESS_FINE_LOCATION permission in AndroidManifest and request runtime permissions.",
            "docs_link": "https://reactnative.dev/docs/geolocation"
        },
        {
            "regex": re.compile(r'\bCameraRoll\b'),
            "api_name": "CameraRoll",
            "ios_usage": "Used to access photos on iOS.",
            "android_considerations": "Request READ_EXTERNAL_STORAGE permission on Android. Consider react-native-cameraroll for cross-platform usage.",
            "docs_link": "https://github.com/react-native-cameraroll/react-native-cameraroll"
        },
        {
            "regex": re.compile(r'react-native-fs'),
            "api_name": "react-native-fs",
            "ios_usage": "Used for file operations on iOS.",
            "android_considerations": "Add WRITE_EXTERNAL_STORAGE permission and handle scoped storage on Android.",
            "docs_link": "https://github.com/itinance/react-native-fs"
        }
    ]

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".js") or file.endswith(".tsx"):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    for pat in patterns:
                        if pat["regex"].search(content):
                            api_issues.append({
                                "api_name": pat["api_name"],
                                "ios_usage": pat["ios_usage"],
                                "android_considerations": pat["android_considerations"],
                                "docs_link": pat["docs_link"]
                            })
                except Exception:
                    pass

    # Deduplicate if needed
    # Convert to a set of tuples and back to list if duplication is a concern.
    unique_issues = []
    seen = set()
    for issue in api_issues:
        key = (issue["api_name"], issue["ios_usage"], issue["android_considerations"], issue["docs_link"])
        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)

    return unique_issues

def analyze_assets(project_path):
    """
    Lists assets, detects iOS @2x/@3x images, and suggests Android drawable directories.

    Heuristics:
      - If file name contains @2x: suggest drawable-hdpi
      - If file name contains @3x: suggest drawable-xxhdpi
      - Provide docs link for Android drawable resources.
    """

    asset_issues = []
    drawable_docs = "https://developer.android.com/guide/topics/resources/drawable-resource"

    # Mapping iOS @x scale to Android drawable buckets
    scale_mapping = {
        "@2x": "drawable-hdpi",
        "@3x": "drawable-xxhdpi",
        "@4x": "drawable-xxxhdpi"
    }

    # Consider common image extensions
    image_extensions = (".png", ".jpg", ".jpeg")

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.lower().endswith(image_extensions):
                file_path = os.path.join(root, file)
                ios_variant = ""
                android_recommendation = ""

                for scale, folder in scale_mapping.items():
                    if scale in file:
                        ios_variant = scale
                        # Suggest placing a scaled version of the image in the corresponding folder
                        base_name = file.replace(scale, "")  # strip @2x or @3x from filename
                        android_recommendation = f"Place a scaled version of {base_name} in {folder} folder."
                        break

                if ios_variant:
                    asset_issues.append({
                        "asset_path": file_path,
                        "asset_type": "image",
                        "ios_variant": ios_variant,
                        "android_recommendation": android_recommendation,
                        "docs_link": drawable_docs
                    })

    return asset_issues

def analyze_testing_coverage(project_path):
    """
    Heuristic approach:
      - For each component file (e.g., *.js, *.tsx in screens/components dir),
        check if there's a corresponding test file (*.test.js, *.spec.js).
      - If no test file is found, consider test coverage low.
      - If iOS-specific logic is found (`Platform.OS === 'ios'`) and no tests,
        suggest adding Android tests.
    """

    component_files = []
    test_files = set()

    ios_check_pattern = re.compile(r'Platform\.OS\s*===\s*[\'"]ios[\'"]')

    # Gather component and test files
    for root, _, files in os.walk(project_path):
        for file in files:
            if (file.endswith(".js") or file.endswith(".tsx")) and "node_modules" not in root:
                file_path = os.path.join(root, file)
                # Consider any file not ending in .test or .spec as a component file
                # This is simplistic; adjust as needed.
                if not (".test." in file or ".spec." in file):
                    component_files.append(file_path)
                else:
                    test_files.add(file_path)

    coverage_issues = []
    testing_docs = "https://reactnative.dev/docs/testing-overview"

    for c_file in component_files:
        base_name = os.path.splitext(os.path.basename(c_file))[0]
        # Look for a corresponding test file like MyComponent.test.js or MyComponent.spec.js
        test_for_component_found = False
        for t in test_files:
            if base_name in os.path.basename(t):
                test_for_component_found = True
                break

        # If no test found, record issue
        if not test_for_component_found:
            ios_logic = False
            try:
                with open(c_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if ios_check_pattern.search(content):
                        ios_logic = True
            except Exception:
                pass

            coverage_issues.append({
                "component_name": base_name,
                "test_coverage_percentage": 0.0,
                "ios_specific_functionality": "Yes" if ios_logic else "No",
                "android_testing_suggestions": (
                    "Add Jest/React Native Testing Library tests focusing on Android behavior. "
                    "If using ios-specific logic, ensure Android code paths are tested. Consider Detox or Appium for integration tests."
                ),
                "docs_link": testing_docs
            })

    return coverage_issues

def analyze_permissions(project_path):
    """
    Maps known iOS Info.plist keys to Android permissions.
    Heuristics:
      - NSCameraUsageDescription -> CAMERA
      - NSLocationWhenInUseUsageDescription -> ACCESS_FINE_LOCATION
      - NSPhotoLibraryUsageDescription -> READ_EXTERNAL_STORAGE
    """

    ios_to_android = {
        "NSCameraUsageDescription": ("android.permission.CAMERA", "Add <uses-permission android:name=\"android.permission.CAMERA\"/> to AndroidManifest.xml"),
        "NSLocationWhenInUseUsageDescription": ("android.permission.ACCESS_FINE_LOCATION", "Add <uses-permission android:name=\"android.permission.ACCESS_FINE_LOCATION\"/> to AndroidManifest.xml"),
        "NSPhotoLibraryUsageDescription": ("android.permission.READ_EXTERNAL_STORAGE", "Add <uses-permission android:name=\"android.permission.READ_EXTERNAL_STORAGE\"/> to AndroidManifest.xml")
    }

    perms_issues = []
    permission_docs = "https://developer.android.com/guide/topics/permissions/overview"

    # Search for a Info.plist or any .plist files
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".plist"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        for ios_key, (android_perm, note) in ios_to_android.items():
                            if ios_key in content:
                                perms_issues.append({
                                    "ios_permission": ios_key,
                                    "android_permission": android_perm,
                                    "notes": note,
                                    "docs_link": permission_docs
                                })
                except Exception:
                    pass

    return perms_issues

def analyze_build_recommendations(project_path):
    """
    Suggest Gradle configs, Android emulator setup, and React Native Android linking recommendations.
    Heuristics:
      - If Podfile or ios directory found, suggest setting up build.gradle in android folder.
      - Always suggest creating local.properties and ensuring Android SDK path is set.
      - Suggest using AVD (Android Virtual Device) for testing.
    """

    build_recs = []
    gradle_docs = "https://developer.android.com/studio/build"
    rn_android_setup = "https://reactnative.dev/docs/environment-setup"
    emulator_docs = "https://developer.android.com/studio/run/emulator"

    # Check if ios directory or Podfile exists as a sign of iOS build environment
    ios_env_detected = False

    for root, dirs, files in os.walk(project_path):
        if 'ios' in dirs:
            ios_env_detected = True
        for file in files:
            if file.lower() == "podfile":
                ios_env_detected = True

    # If ios environment detected, add recommendation to setup Android build
    if ios_env_detected:
        build_recs.append({
            "aspect": "Build Configuration",
            "recommendation": "Add an android folder with build.gradle settings. Use gradlew to build for Android.",
            "docs_link": gradle_docs
        })

    # General recommendations
    build_recs.append({
        "aspect": "SDK Setup",
        "recommendation": "Ensure local.properties contains sdk.dir pointing to Android SDK. Install Android platform tools.",
        "docs_link": rn_android_setup
    })

    build_recs.append({
        "aspect": "Emulator Testing",
        "recommendation": "Use AVD Manager or Android Studio to create an Android Virtual Device for testing.",
        "docs_link": emulator_docs
    })

    build_recs.append({
        "aspect": "Performance",
        "recommendation": "Consider enabling Hermes on Android for better performance.",
        "docs_link": "https://reactnative.dev/docs/hermes"
    })

    return build_recs

def analyze_gestures_and_native_modules(project_path):
    """
    Map iOS gestures to Android equivalents:
    - Detect mentions of `3D Touch` or `force touch` in code/comments.
      Suggest long-press or contextual menus for Android.

    Detect iOS native modules:
    - If `.m` or `.mm` files are found in ios directory, suggest creating equivalent Android native modules in Java/Kotlin.
    - Provide bridging guidance link.
    """

    gestures_issues = []
    native_modules_issues = []

    # Gesture patterns
    gesture_patterns = [
        (re.compile(r'\bforce touch\b', re.IGNORECASE), "force touch -> long-press on Android"),
        (re.compile(r'\b3D Touch\b', re.IGNORECASE), "3D Touch -> long-press or contextual menu on Android")
    ]

    bridging_docs = "https://reactnative.dev/docs/native-modules-android"

    ios_modules_found = False
    for root, dirs, files in os.walk(project_path):
        # Check for .m or .mm files in an ios directory as sign of native iOS modules
        if 'ios' in root.lower():
            for file in files:
                if file.endswith(".m") or file.endswith(".mm"):
                    ios_modules_found = True

        for file in files:
            if file.endswith(".js") or file.endswith(".tsx"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    for pattern, suggestion in gesture_patterns:
                        if pattern.search(content):
                            gestures_issues.append({
                                "ios_gesture": pattern.pattern,
                                "android_equivalent": suggestion,
                                "notes": "Replace iOS-specific gesture with Android-friendly alternative.",
                                "docs_link": "https://developer.android.com/training/gestures"
                            })
                except:
                    pass

    if ios_modules_found:
        # Suggest creating Android native modules
        native_modules_issues.append({
            "ios_module": "Custom iOS Native Module(s)",
            "android_equivalent": "Create Android native module in Java/Kotlin",
            "bridging_guidance": "Refer to React Native docs for Android native modules.",
            "docs_link": bridging_docs
        })

    return {
        "gestures": gestures_issues,
        "native_modules": native_modules_issues
    }


def analyze_progress(project_path):
    components_ported = 0
    ios_libs_replaced = 0
    apis_adjusted = 0
    ui_elements_converted = 0

    # Check for screens
    # Assuming screens are .js/.tsx files in src/screens or src/features/*/screens
    # Just count them
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if (file.endswith(".js") or file.endswith(".tsx")) and "node_modules" not in root:
                if "screen" in file.lower():
                    components_ported += 1

            # Check for assets @2x/@3x
            if "@2x" in file or "@3x" in file:
                ui_elements_converted += 1

            # Check for .m/.mm (iOS native modules)
            if file.endswith(".m") or file.endswith(".mm"):
                ios_libs_replaced += 1

    # If we found API patterns in analyze_api_behavior previously, we could integrate here.
    # For now, let's say if ios_libs_replaced > 0, we consider that we adjusted some APIs too
    if ios_libs_replaced > 0:
        apis_adjusted = ios_libs_replaced  # heuristic

    return {
        "components_ported": components_ported,
        "ios_libs_replaced": ios_libs_replaced,
        "apis_adjusted": apis_adjusted,
        "ui_elements_converted": ui_elements_converted
    }

def analyze_performance_issues(project_path):
    """
    Detect performance issues:
      - Look for `requestAnimationFrame` usage
      - Look for `Animated` usage patterns repeated multiple times
    """

    perf_issues = []
    perf_docs = "https://reactnative.dev/docs/optimizing-flatlist-configuration"

    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith(".js") or file.endswith(".tsx"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    rAF_count = content.count("requestAnimationFrame")
                    animated_count = content.count("Animated.timing")

                    # If multiple requestAnimationFrame or multiple Animated calls found:
                    if rAF_count > 5 or animated_count > 5:
                        perf_issues.append({
                            "file_path": file_path,
                            "issue_type": "performance_hotspot",
                            "details": (
                                f"High usage of animations or requestAnimationFrame detected "
                                f"(requestAnimationFrame: {rAF_count}, Animated.timing: {animated_count}). "
                                "Consider optimizing animations or using InteractionManager."
                            ),
                            "docs_link": perf_docs
                        })
                except:
                    pass

    return perf_issues