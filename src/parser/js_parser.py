import os
import re

def is_screen_file(file_path):
    # Checks if 'screens' is in path and filename ends with 'Screen'
    # Also consider src/features/**/screens/** and src/screens/**
    file_path_lower = file_path.lower()
    filename = os.path.splitext(os.path.basename(file_path))[0]

    if "screens" in file_path_lower and filename.endswith("Screen"):
        return True
    return False

def parse_screens(project_path):
    visited_files = set()
    route_to_component = parse_navigators(project_path, visited_files)

    # Find which files define these components
    component_to_file = find_component_files(project_path, route_to_component.values())

    screens = []
    navigation_edges = []

    identified_screen_files = set(component_to_file.values())

    # Consider fallback heuristic screens
    # Any file in known screen directories or matching naming convention
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".js") or file.endswith(".tsx"):
                file_path = os.path.join(root, file)
                if (file_path in identified_screen_files 
                    or is_screen_file(file_path)
                    or in_screen_directory(file_path)):
                    screen_name = os.path.splitext(file)[0]
                    nav_info = analyze_navigation(file_path)

                    screens.append({
                        "name": screen_name,
                        "type": "screen",
                        "file_path": file_path,
                        "dependencies": nav_info["dependencies"]
                    })

                    navigation_edges.extend(nav_info["navigation_edges"])

    return screens, navigation_edges

def in_screen_directory(file_path):
    # Heuristic: if file is under src/features/**/screens/** or src/screens/**
    # Adjust as needed for your project structure
    lowered = file_path.lower()
    if "src/screens/" in lowered:
        return True
    if "src/features/" in lowered and "/screens/" in lowered:
        return True
    return False

def parse_navigators(project_path, visited):
    """
    Recursively parse navigation files to find screen declarations in JSX and object form.
    """
    route_to_component = {}
    navigation_dir = os.path.join(project_path, "src", "navigation")
    search_dir = navigation_dir if os.path.exists(navigation_dir) else project_path

    # Include common navigator types: Stack, Drawer, Tab, MaterialTopTab, NativeStack
    navigator_names = ['Stack', 'Drawer', 'Tab', 'MaterialTopTab', 'NativeStack']
    navigator_pattern = '|'.join(navigator_names)

    # JSX pattern: <Stack.Screen name="Home" component={HomeScreen} />
    screen_pattern = re.compile(
        rf'<(?:{navigator_pattern})\.Screen\s+name=["\'](.*?)["\']\s+component=\{{(.*?)\}}'
    )

    # Object-based route pattern: createStackNavigator({ Home: HomeScreen, Profile: ProfileScreen })
    # We'll capture the entire object and then parse line by line.
    object_route_pattern = re.compile(r'create\w*Navigator\(\s*\{([\s\S]*?)\}\)')

    # Lines inside object config: Home: HomeScreen,
    component_line_pattern = re.compile(r'(\w+)\s*:\s*([A-Za-z0-9_]+)\s*,?')

    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.endswith(".js") or file.endswith(".tsx"):
                file_path = os.path.join(root, file)
                if file_path in visited:
                    continue
                visited.add(file_path)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                        # JSX-based screens
                        matches = screen_pattern.findall(content)
                        for route, component in matches:
                            route_to_component[route] = component
                            if is_navigator(component):
                                nested_files = find_component_definition_files(project_path, component)
                                for nf in nested_files:
                                    nested_routes = parse_navigators_for_file(nf, visited)
                                    route_to_component.update(nested_routes)

                        # Object-based routes
                        obj_matches = object_route_pattern.findall(content)
                        for obj_content in obj_matches:
                            line_matches = component_line_pattern.findall(obj_content)
                            for route, component in line_matches:
                                route_to_component[route] = component
                                if is_navigator(component):
                                    nested_files = find_component_definition_files(project_path, component)
                                    for nf in nested_files:
                                        nested_routes = parse_navigators_for_file(nf, visited)
                                        route_to_component.update(nested_routes)
                except Exception as e:
                    print(f"Error parsing navigator at {file_path}: {e}")

    return route_to_component

def parse_navigators_for_file(file_path, visited):
    route_to_component = {}
    navigator_names = ['Stack', 'Drawer', 'Tab', 'MaterialTopTab', 'NativeStack']
    navigator_pattern = '|'.join(navigator_names)
    screen_pattern = re.compile(
        rf'<(?:{navigator_pattern})\.Screen\s+name=["\'](.*?)["\']\s+component=\{{(.*?)\}}'
    )

    object_route_pattern = re.compile(r'create\w*Navigator\(\s*\{([\s\S]*?)\}\)')
    component_line_pattern = re.compile(r'(\w+)\s*:\s*([A-Za-z0-9_]+)\s*,?')

    if file_path in visited:
        return route_to_component
    visited.add(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

            # JSX-based screens
            matches = screen_pattern.findall(content)
            for route, component in matches:
                route_to_component[route] = component
                if is_navigator(component):
                    nested_files = find_component_definition_files(os.path.dirname(file_path), component)
                    for nf in nested_files:
                        nested_routes = parse_navigators_for_file(nf, visited)
                        route_to_component.update(nested_routes)

            # Object-based routes
            obj_matches = object_route_pattern.findall(content)
            for obj_content in obj_matches:
                line_matches = component_line_pattern.findall(obj_content)
                for route, component in line_matches:
                    route_to_component[route] = component
                    if is_navigator(component):
                        nested_files = find_component_definition_files(os.path.dirname(file_path), component)
                        for nf in nested_files:
                            nested_routes = parse_navigators_for_file(nf, visited)
                            route_to_component.update(nested_routes)

    except Exception as e:
        print(f"Error parsing navigator at {file_path}: {e}")

    return route_to_component

def is_navigator(component_name):
    return re.search(r'(Navigator|Stack|Drawer|Tab)$', component_name) is not None

def find_component_definition_files(project_path, component_name):
    """
    Attempt to locate files where a component might be defined.
    Consider dynamic imports and lazy loading as well.
    """
    found_files = []
    # Patterns for direct exports
    export_patterns = [
        re.compile(rf'export default function\s+{component_name}\s*\('),
        re.compile(rf'export function\s+{component_name}\s*\('),
        re.compile(rf'export default\s+{component_name}\s*(;|\n|\r|$)'),
        re.compile(rf'function\s+{component_name}\s*\(')
    ]

    # Consider React.lazy(() => import('...')) patterns for dynamic imports
    lazy_pattern = re.compile(rf'{component_name}\s*=\s*React\.lazy\(\s*\(\)\s*=>\s*import\(["\'](.*?)["\']\)\s*\)')

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".js") or file.endswith(".tsx"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                        found = False
                        for pattern in export_patterns:
                            if pattern.search(content):
                                found_files.append(file_path)
                                found = True
                                break
                        if not found:
                            lazy_match = lazy_pattern.search(content)
                            if lazy_match:
                                # If we have a lazy import, try to resolve that path
                                imported_path = lazy_match.group(1)
                                # Resolve relative import
                                full_path = resolve_import_path(root, imported_path)
                                if full_path and os.path.exists(full_path):
                                    found_files.append(full_path)
                except:
                    pass

    return found_files

def resolve_import_path(current_dir, imported_path):
    # A simple resolver: if imported_path starts with './' or '../', join paths
    # If absolute or from node_modules, you'd need more logic
    if imported_path.startswith('.') or imported_path.startswith('..'):
        return os.path.normpath(os.path.join(current_dir, imported_path))
    # If absolute paths or special aliases are used, you'd need custom logic
    return None

def find_component_files(project_path, component_names):
    """
    Given a list of component names, find which files define them.
    """
    component_to_file = {}
    component_names = set(component_names)

    export_patterns = [
        re.compile(r'export default function\s+([A-Za-z0-9_]+)\s*\('),
        re.compile(r'export function\s+([A-Za-z0-9_]+)\s*\('),
        re.compile(r'export default\s+([A-Za-z0-9_]+)\s*(;|\n|\r|$)'),
        re.compile(r'function\s+([A-Za-z0-9_]+)\s*\(')
    ]

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".js") or file.endswith(".tsx"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                        found_components = set()
                        for pattern in export_patterns:
                            for match in pattern.findall(content):
                                name = match[0] if isinstance(match, tuple) else match
                                found_components.add(name)

                        # If any found component is in component_names, map it
                        for c in found_components:
                            if c in component_names:
                                component_to_file[c] = file_path
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

    return component_to_file

def analyze_navigation(file_path):
    """
    Parses a screen file to extract navigation actions and dependencies.
    Expanded logic:
    - Detect navigation via this.props.navigation, props.navigation, useNavigation hook, etc.
    - Consider navigate, push, replace, reset, goBack, popToTop
      (Though goBack/popToTop have no target screen, we may skip them)
    """
    navigation_edges = []
    dependencies = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

            # Extract imports
            for line in content.split('\n'):
                if line.strip().startswith("import "):
                    dependencies.append(line.strip())

            # Potential navigation variable patterns:
            # Class Components: this.props.navigation
            # Function Components: props.navigation
            # Hooks: const navigation = useNavigation();
            # We'll search for calls like navigation.navigate('Target'), props.navigation.push('Target') etc.

            # We'll gather a list of regexes for navigation calls:
            # Patterns:
            # navigation variable patterns: `navigation.navigate("Route")`, `props.navigation.push('Route')`, `this.props.navigation.replace('Route')`
            # We'll capture (action, target) pairs. 
            nav_patterns = [
                # Hook or variable-based navigation: navigation.navigate('Route')
                re.compile(r'(?:navigation|props\.navigation|this\.props\.navigation)\.(navigate|push|replace|reset)\(["\'](.*?)["\']'),
                
                # Direct navigate(...) calls if any (rare without variable):
                re.compile(r'(navigate|push|replace|reset)\(["\'](.*?)["\']'),

                # If they do something like const { navigate } = navigation; navigate('Route')
                re.compile(r'\b(navigate|push|replace|reset)\(["\'](.*?)["\']')
            ]

            # Also consider .goBack() and .popToTop() - though these may not yield a target route
            # We won't create edges for those since no explicit target route.
            # If needed:
            # goBack_pattern = re.compile(r'(?:navigation|props\.navigation|this\.props\.navigation)\.(goBack|popToTop)\(')

            # We'll search all patterns in the file content
            found = set()
            for pat in nav_patterns:
                for match in pat.findall(content):
                    action, target = match
                    if target:  # Only consider if we have a target route
                        found.add((action, target))

            # If using useNavigation:
            # Look for `const navigation = useNavigation();` and then `navigation.navigate('Route')`
            # Our patterns above might already catch these calls if `navigation` is used.
            # But let's ensure we handle it specifically if needed:
            if 'useNavigation(' in content:
                # If navigation variable is set:
                # const navigation = useNavigation();
                # Then search for navigation.navigate('X')
                hook_pattern = re.compile(r'navigation\.(navigate|push|replace|reset)\(["\'](.*?)["\']')
                for m in hook_pattern.findall(content):
                    action, target = m
                    if target:
                        found.add((action, target))

            # Now add these found edges
            # Source screen is inferred from filename
            source_screen = os.path.splitext(os.path.basename(file_path))[0]
            for (action, target_screen) in found:
                navigation_edges.append({
                    "source": source_screen,
                    "target": target_screen,
                    "action": action
                })

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return {
        "dependencies": ", ".join(dependencies),
        "navigation_edges": navigation_edges
    }
