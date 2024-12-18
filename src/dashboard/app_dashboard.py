import sys
import os
import logging
import streamlit as st
import pandas as pd
from pyvis.network import Network
from streamlit.components.v1 import html
from src.db.database import get_db_connection

st.set_page_config(page_title="React Native App Analysis", layout="wide")
logging.basicConfig(level=logging.INFO)

# Authentication
USERNAME = os.getenv("DASHBOARD_USERNAME")
PASSWORD = os.getenv("DASHBOARD_PASSWORD")

# Helper functions
def authenticate_user():
    """Authenticate user with a dedicated login screen"""
    st.title("🔒 Login")
    st.write("Please enter your credentials to access the dashboard.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if username == USERNAME and password == PASSWORD:
        st.success("Authentication successful! Please refresh the page or continue.")
        st.session_state["authenticated"] = True
        return True
    elif username or password:  # Only display error if inputs are provided
        st.error("Invalid username or password")
    return False

def get_database_data(query):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return []

def show_screens():
    st.header("📱 Screens")
    st.write("These are the screens identified in your iOS/React Native project. Use this as a reference to ensure all screens have Android-friendly layouts and navigations.")
    query = "SELECT * FROM screens"
    screens = get_database_data(query)
    if screens:
        df = pd.DataFrame(screens, columns=["ID", "Name", "Type", "File Path", "Dependencies", "Created At"])
        search_term = st.text_input("Search Screens by Name or Path", "")
        filtered_df = df[
            df["Name"].str.contains(search_term, case=False, na=False) | 
            df["File Path"].str.contains(search_term, case=False, na=False)
        ]
        st.dataframe(filtered_df)
        st.write("Tip: Identify if any screen relies heavily on iOS-only components and check UI Patterns or Platform Issues sections.")
    else:
        st.write("No screens found.")

def show_api_calls():
    st.header("🌐 API Calls")
    st.write("These are the API calls detected. Some may require different permissions or handling on Android.")
    query = "SELECT * FROM api_calls"
    api_calls = get_database_data(query)
    if api_calls:
        df = pd.DataFrame(api_calls, columns=["ID","Endpoint","Method","Request Body","Associated Screen ID","Created At"])
        st.dataframe(df)
        st.write("Consider if any of these APIs need Android-specific permission (check the Permissions tab) or different handling (API Behavior tab).")
    else:
        st.write("No API calls found.")

def show_dependencies():
    st.header("🔗 Dependencies")
    st.write("These are the project dependencies. Identify iOS-specific libraries and find Android equivalents.")
    query = "SELECT * FROM dependencies"
    deps = get_database_data(query)
    if deps:
        df = pd.DataFrame(deps, columns=["ID","Source","Target","Type","File Path","Created At"])
        st.dataframe(df)
        st.write("Check Platform Issues and UI Patterns sections for hints on replacing iOS-specific deps.")
    else:
        st.write("No dependencies found.")

def show_navigation_paths():
    st.header("🛠️ Navigation Paths")
    st.write("This visualizes your app's navigation flow. Use it to find screens with missing Android equivalents or problematic platform-specific patterns.")
    query_paths = "SELECT * FROM navigation_paths"
    paths = get_database_data(query_paths)
    query_issues = "SELECT file_path FROM platform_issues"
    platform_issues = get_database_data(query_issues)

    if not paths:
        st.write("No navigation paths found.")
        return

    nav_df = pd.DataFrame(paths, columns=["ID","Source Screen","Target Screen","Action","Created At"])
    issues_df = pd.DataFrame(platform_issues, columns=["File Path"])

    incoming_counts = nav_df["Target Screen"].value_counts()
    outgoing_counts = nav_df["Source Screen"].value_counts()

    all_screens = set(nav_df["Source Screen"].unique()).union(set(nav_df["Target Screen"].unique()))
    summary_data = []
    for screen in all_screens:
        incoming = incoming_counts.get(screen,0)
        outgoing = outgoing_counts.get(screen,0)
        notes = []
        if incoming == 0:
            notes.append("Entry Point")
        if outgoing == 0:
            notes.append("Dead End")
        if any(screen in path for path in issues_df["File Path"].unique()):
            notes.append("Platform Issues ⚠️")
        summary_data.append({"Screen Name":screen,"Incoming Paths":incoming,"Outgoing Paths":outgoing,"Notes":", ".join(notes)})

    st.write("### Navigation Summary")
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df.sort_values(by=["Incoming Paths","Outgoing Paths"],ascending=[True,False]))

    st.write("### Filters")
    top_sources = nav_df["Source Screen"].value_counts().head(10).index.tolist()
    selected_source = st.selectbox("Select a Top-Level Source Screen", ["All"] + top_sources)
    max_paths = st.slider("Number of Paths to Display", 10, 200, 50, step=10)

    filtered_df = nav_df if selected_source == "All" else nav_df[nav_df["Source Screen"] == selected_source]
    filtered_df = filtered_df.head(max_paths)
    st.write(f"Showing {len(filtered_df)} paths")
    st.dataframe(filtered_df)

    if not filtered_df.empty:
        st.subheader("Interactive Navigation Flow")
        visualize_navigation_flow(filtered_df, issues_df)
        st.write("Red nodes indicate platform-specific issues on that screen. Check 'Platform Issues' and 'UI Patterns' to resolve them.")
    else:
        st.write("No navigation paths match the current filters.")

def visualize_navigation_flow(nav_df, issues_df):
    net = Network(height="750px", width="100%", directed=True)
    nodes = set(nav_df['Source Screen']).union(set(nav_df['Target Screen']))
    problematic_files = issues_df['File Path'].unique()

    for node in nodes:
        color = "red" if any(node in path for path in problematic_files) else "lightblue"
        title = "⚠️ Platform-specific issues detected" if color == "red" else node
        net.add_node(node, label=node, title=title, color=color, size=20)

    for _, row in nav_df.iterrows():
        net.add_edge(row["Source Screen"], row["Target Screen"], title=row["Action"], label=row["Action"], color="gray")

    net.repulsion(node_distance=150, central_gravity=0.5, damping=0.9)
    net_file = "navigation_graph.html"
    net.write_html(net_file)

    with open(net_file,"r",encoding="utf-8") as f:
        html_content = f.read()
        html(html_content,height=750,width=1000)

def show_platform_issues():
    st.header("⚠️ Platform-Specific Issues")
    st.write("These issues highlight where the app uses iOS-only code or patterns. Use suggested Android equivalents or check docs for guidance.")
    query = "SELECT file_path, line_number, issue_type, details, created_at FROM platform_issues"
    issues = get_database_data(query)
    if issues:
        cols = ["File Path","Line Number","Issue Type","Details","Created At"]
        df = pd.DataFrame(issues, columns=cols)
        st.write("### Detailed Platform Issues")
        st.dataframe(df)

        ios_lib_issues = df[df["Issue Type"]=="ios_library"].copy()
        if not ios_lib_issues.empty:
            st.write("### iOS-Only Libraries and Android Equivalents")
            st.write("Consider replacing these libraries with their Android-friendly counterparts.")
            st.dataframe(ios_lib_issues[["File Path","Line Number","Details"]])
        else:
            st.write("No iOS-specific library issues found.")
        st.write("Tip: Check Permissions and API Behavior tabs for additional porting considerations.")
    else:
        st.write("No platform-specific issues found.")

def show_ui_patterns():
    st.header("UI Patterns")
    st.write("Below are iOS-specific UI patterns and their Android equivalents, along with actionable guidance to speed up the porting process.")
    query = "SELECT screen_name, pattern_type, suggested_android, details, created_at FROM ui_patterns"
    data = get_database_data(query)

    pattern_guidance = {
        "TabBar": (
            "Use BottomNavigationView for Android. Replace TabBarIOS with a cross-platform navigation library.",
            "https://material.io/components/bottom-navigation"
        ),
        "NavigationController": (
            "Use a Drawer or Stack navigator in React Navigation for Android. Replace NavigationController with React Navigation stacks or drawers.",
            "https://reactnavigation.org/"
        ),
        "Modal": (
            "Replace <Modal> with DialogFragment or AlertDialog on Android. Consider react-native-modal or Material dialogs.",
            "https://developer.android.com/guide/fragments/dialogs"
        )
    }

    if data:
        df = pd.DataFrame(data, columns=["Screen Name","Pattern Type","Suggested Android","Details","Created At"])
        recommended_actions = []
        docs_links = []

        for _, row in df.iterrows():
            p_type = row["Pattern Type"]
            if p_type in pattern_guidance:
                action, docs = pattern_guidance[p_type]
                recommended_actions.append(action)
                docs_links.append(docs)
            else:
                recommended_actions.append("No specific guidance available.")
                docs_links.append("")

        df["Recommended Action"] = recommended_actions
        df["Docs/Links"] = docs_links

        st.dataframe(df[["Screen Name","Pattern Type","Suggested Android","Details","Recommended Action","Docs/Links","Created At"]])
        st.write("Focus on replacing these patterns early to align with Android’s UI/UX guidelines.")
    else:
        st.write("No UI patterns found.")

def show_device_styling():
    st.header("Device Styling & Design")
    st.write("These issues highlight hardcoded px values, non-material components, or styling that doesn't fit Android. Consider using dp units and Material Components.")
    query = "SELECT file_path,line_number,issue_type,details,created_at FROM device_styling"
    data = get_database_data(query)
    if data:
        df = pd.DataFrame(data, columns=["File Path","Line Number","Issue Type","Details","Created At"])
        st.dataframe(df)
        st.write("Check Material Design guidelines and use dp/sp units for responsive UI.")
    else:
        st.write("No device styling issues found.")

def show_api_behavior():
    st.header("API Behavior Differences")
    st.write("These APIs behave differently or require extra steps on Android. Review the considerations and docs to ensure smooth migration.")
    query = "SELECT api_name, ios_usage, android_considerations, docs_link, created_at FROM api_behavior"
    data = get_database_data(query)
    if data:
        df = pd.DataFrame(data, columns=["API Name","iOS Usage","Android Considerations","Docs Link","Created At"])
        st.dataframe(df)
        st.write("Implement suggested changes to handle permissions, different file systems, or notification frameworks on Android.")
    else:
        st.write("No API behavior differences found.")

def show_assets():
    st.header("Assets")
    st.write("These are your project's assets. Android uses a drawable-xxxhdpi structure instead of @2x/@3x files. Adjust accordingly.")
    query = "SELECT asset_path, asset_type, ios_variant, android_recommendation, created_at FROM assets"
    data = get_database_data(query)
    if data:
        df = pd.DataFrame(data, columns=["Asset Path","Asset Type","iOS Variant","Android Recommendation","Created At"])
        st.dataframe(df)
        st.write("Convert iOS image assets to Android drawables with appropriate densities.")
    else:
        st.write("No assets found.")

def show_testing_coverage():
    st.header("Testing Coverage")
    st.write("Identify components lacking tests or requiring Android-specific tests (like camera, gestures). Implement Android-friendly test frameworks.")
    query = "SELECT component_name,test_coverage_percentage,ios_specific_functionality,android_testing_suggestions,created_at FROM testing_coverage"
    data = get_database_data(query)
    if data:
        df = pd.DataFrame(data, columns=["Component","Coverage %","iOS Functionality","Android Testing Suggestions","Created At"])
        st.dataframe(df)
        st.write("Consider Jest, Detox, or Appium for Android-specific tests.")
    else:
        st.write("No testing coverage data found.")

def show_permissions():
    st.header("Permissions Mapping")
    st.write("Map iOS Info.plist permissions to AndroidManifest.xml. Add necessary permissions and request flows for Android.")
    query = "SELECT ios_permission,android_permission,notes,created_at FROM permissions_mapping"
    data = get_database_data(query)
    if data:
        df = pd.DataFrame(data, columns=["iOS Permission","Android Permission","Notes","Created At"])
        st.dataframe(df)
        st.write("Update AndroidManifest.xml and consider runtime permission requests for these features.")
    else:
        st.write("No permissions mapping found.")

def show_build_recommendations():
    st.header("Build & Gradle Recommendations")
    st.write("Set up Gradle, Android Studio, and Android emulators. Follow these recommendations for a smooth Android build process.")
    query = "SELECT aspect,recommendation,docs_link,created_at FROM build_recommendations"
    data = get_database_data(query)
    if data:
        df = pd.DataFrame(data, columns=["Aspect","Recommendation","Docs Link","Created At"])
        st.dataframe(df)
        st.write("Implement these suggestions early to streamline the Android build and testing pipeline.")
    else:
        st.write("No build recommendations found.")

def show_gestures():
    st.header("Gestures Mapping")
    st.write("iOS-specific gestures may need to be replaced with Android equivalents (long-press menus, ripple effects).")
    query = "SELECT ios_gesture, android_equivalent, notes, created_at FROM gestures_mapping"
    data = get_database_data(query)
    if data:
        df = pd.DataFrame(data, columns=["iOS Gesture","Android Equivalent","Notes","Created At"])
        st.dataframe(df)
        st.write("Adopt Android's native gesture systems and consider Material ripple effects.")
    else:
        st.write("No gesture mappings found.")

def show_native_modules():
    st.header("Native Modules")
    st.write("If you used native iOS modules, implement equivalent Java/Kotlin modules on Android.")
    query = "SELECT ios_module, android_equivalent, bridging_guidance, created_at FROM native_modules"
    data = get_database_data(query)
    if data:
        df = pd.DataFrame(data, columns=["iOS Module","Android Equivalent","Bridging Guidance","Created At"])
        st.dataframe(df)
        st.write("Follow bridging guidance and consider code-sharing strategies to minimize platform-specific modules.")
    else:
        st.write("No native module mappings found.")

def show_progress_dashboard():
    st.header("Porting Progress Dashboard")
    st.write("Track your progress as you replace iOS libraries, adjust APIs, and convert UI elements to Android. Aim to see these numbers grow as you implement fixes.")
    query = "SELECT components_ported, ios_libs_replaced, apis_adjusted, ui_elements_converted, last_updated FROM progress_dashboard ORDER BY last_updated DESC LIMIT 1"
    data = get_database_data(query)
    if data and len(data)>0:
        df = pd.DataFrame([data[0]], columns=["Components Ported","iOS Libs Replaced","APIs Adjusted","UI Elements Converted","Last Updated"])
        st.dataframe(df)
        st.write("Use this as a motivator and checklist reference. The more you port, the closer you get to a stable Android release!")
    else:
        st.write("No progress data found.")

def show_performance_issues():
    st.header("Performance Issues")
    st.write("Identify platform-specific performance bottlenecks and follow provided recommendations or docs for Android optimizations.")
    query = "SELECT file_path, issue_type, details, created_at FROM performance_issues"
    data = get_database_data(query)
    if data:
        df = pd.DataFrame(data, columns=["File Path","Issue Type","Details","Created At"])
        st.dataframe(df)
        st.write("Optimize animations, memory usage, and consider Android-friendly optimization techniques (lazy-loading, caching).")
    else:
        st.write("No performance issues found.")

def show_porting_checklist():
    st.header("Porting Checklist (Unified Guidance)")
    st.write("""
    This section aggregates key findings and gives you a prioritized checklist:
    1. Address iOS-only UI patterns (UI Patterns tab) and adopt Material design.
    2. Resolve platform issues (Platform Issues tab) and replace iOS-only libs.
    3. Adjust APIs that differ on Android (API Behavior tab) and set permissions (Permissions tab).
    4. Convert assets for Android densities (Assets tab).
    5. Update build processes (Build Recommendations tab).
    6. Improve testing coverage for Android scenarios (Testing Coverage tab).
    7. Check gestures and native modules to ensure Android support (Gestures, Native Modules tabs).
    8. Track progress in the Progress Dashboard tab.
    9. Fix performance issues and follow recommended docs.
    """)
    st.write("Use the side menu to deep-dive into each category, then return here to ensure all steps are completed.")

def main():
    """Main function to enforce authentication and display app"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"] or authenticate_user():
        st.title("📊 Enhanced React Native App Analysis Dashboard")
        st.write("Welcome! This dashboard provides a comprehensive analysis of your React Native app, focusing on porting from iOS to Android.")

        menu = [
            "Porting Checklist",
            "Screens", "API Calls", "Dependencies", "Navigation Paths", "Platform Issues",
            "UI Patterns", "Device Styling", "API Behavior", "Assets", "Testing Coverage",
            "Permissions", "Build Recommendations", "Gestures", "Native Modules", "Progress Dashboard", "Performance Issues"
        ]
        choice = st.sidebar.selectbox("Select a Section", menu)

        if choice == "Screens":
            show_screens()
        elif choice == "API Calls":
            show_api_calls()
        elif choice == "Dependencies":
            show_dependencies()
        elif choice == "Navigation Paths":
            show_navigation_paths()
        elif choice == "Platform Issues":
            show_platform_issues()
        elif choice == "UI Patterns":
            show_ui_patterns()
        elif choice == "Device Styling":
            show_device_styling()
        elif choice == "API Behavior":
            show_api_behavior()
        elif choice == "Assets":
            show_assets()
        elif choice == "Testing Coverage":
            show_testing_coverage()
        elif choice == "Permissions":
            show_permissions()
        elif choice == "Build Recommendations":
            show_build_recommendations()
        elif choice == "Gestures":
            show_gestures()
        elif choice == "Native Modules":
            show_native_modules()
        elif choice == "Progress Dashboard":
            show_progress_dashboard()
        elif choice == "Performance Issues":
            show_performance_issues()
        elif choice == "Porting Checklist":
            show_porting_checklist()
    else:
        st.stop()


if __name__ == "__main__":
    main()