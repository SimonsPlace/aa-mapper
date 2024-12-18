import sys
import os
import logging
import streamlit as st
import pandas as pd
import time
from pyvis.network import Network
from streamlit.components.v1 import html
from src.db.database import get_db_connection

st.set_page_config(page_title="React Native App Analysis", layout="wide")
logging.basicConfig(level=logging.INFO)

# Authentication
USERNAME = os.getenv("DASHBOARD_USERNAME")
PASSWORD = os.getenv("DASHBOARD_PASSWORD")

class DatabaseManager:
    @staticmethod
    def execute_query(query, params=None):
        """Execute a database query and return results"""
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    return cursor.fetchall()
        except Exception as e:
            logging.error(f"Database error: {e}")
            return []


class CommentManager:
    @staticmethod
    def add_comment(section_name, related_id, comment_text):
        """Add a new comment"""
        try:
            query = """
                INSERT INTO comments (finding_type, finding_id, comment)
                VALUES (%s, %s, %s)
                RETURNING created_at
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (section_name, related_id, comment_text))
                    created_at = cursor.fetchone()[0]
                    conn.commit()
                    return True, created_at
        except Exception as e:
            logging.error(f"Error adding comment: {e}")
            return False, None

    @staticmethod
    def fetch_comments(section_name, related_id=None):
        """Fetch comments for a section"""
        try:
            query = """
                SELECT comment, created_at 
                FROM comments 
                WHERE finding_type = %s
                """ + (" AND finding_id = %s" if related_id else "") + """
                ORDER BY created_at DESC
            """
            params = (section_name,) + ((related_id,) if related_id else ())
            
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching comments: {e}")
            return []

    @staticmethod
    def display_comments(section_name, related_id=None):
        """Display comments section with input"""
        comments = CommentManager.fetch_comments(section_name, related_id)
        
        st.subheader("Comments")
        if comments:
            for comment, created_at in comments:
                st.markdown(f"- **{created_at}**: {comment}")
        else:
            st.write("No comments yet.")

        # Create a form for comment submission
        with st.form(key=f"comment_form_{section_name}_{related_id}"):
            comment_text = st.text_area("Add a comment:")
            submit_button = st.form_submit_button("Submit Comment")
            
            if submit_button and comment_text.strip():
                success, created_at = CommentManager.add_comment(section_name, related_id, comment_text.strip())
                if success:
                    st.success("Comment added successfully!")
                    # Use time.sleep to show the success message briefly
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to add comment. Please try again.")

    @staticmethod
    def get_all_comments():
        """Fetch all comments with their context data"""
        query = """
            SELECT 
                c.id,
                c.finding_type,
                c.finding_id,
                c.comment,
                c.created_at,
                CASE 
                    WHEN c.finding_type = 'Screens' THEN s.name
                    WHEN c.finding_type = 'API Calls' THEN a.endpoint
                    -- Add more cases for other types as needed
                    ELSE NULL
                END as context_data
            FROM comments c
            LEFT JOIN screens s ON c.finding_type = 'Screens' AND c.finding_id = s.id
            LEFT JOIN api_calls a ON c.finding_type = 'API Calls' AND c.finding_id = a.id
            ORDER BY c.created_at DESC
        """
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching all comments: {e}")
            return []

    @staticmethod
    def update_comment(comment_id, new_text):
        """Update an existing comment"""
        try:
            query = """
                UPDATE comments 
                SET comment = %s,
                    created_at = NOW()
                WHERE id = %s
                RETURNING created_at
            """
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (new_text, comment_id))
                    created_at = cursor.fetchone()[0]
                    conn.commit()
                    return True, created_at
        except Exception as e:
            logging.error(f"Error updating comment: {e}")
            return False, None

    @staticmethod
    def delete_comment(comment_id):
        """Delete a comment"""
        try:
            query = "DELETE FROM comments WHERE id = %s"
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (comment_id,))
                    conn.commit()
                    return True
        except Exception as e:
            logging.error(f"Error deleting comment: {e}")
            return False
            
class DataDisplay:
    @staticmethod
    def show_dataframe(query, columns, title, section_name=None, additional_info=None):
        """Generic method to display data in a dataframe with optional comments"""
        if title:
            st.header(title)
        if additional_info:
            st.write(additional_info)
            
        data = DatabaseManager.execute_query(query)
        if data:
            df = pd.DataFrame(data, columns=columns)
            st.dataframe(df)
            
            if section_name:
                selected_item = st.selectbox(f"Select a {section_name} to comment on", df.iloc[:, 0])
                CommentManager.display_comments(section_name, selected_item)
            return df
        else:
            st.write(f"No {section_name or 'data'} found.")
            if section_name:
                CommentManager.display_comments(section_name)
            return None

class NavigationFlow:
    @staticmethod
    def analyze_paths(nav_df, issues_df):
        """Analyze navigation paths and create summary"""
        incoming_counts = nav_df["Target Screen"].value_counts()
        outgoing_counts = nav_df["Source Screen"].value_counts()
        all_screens = set(nav_df["Source Screen"].unique()).union(set(nav_df["Target Screen"].unique()))
        
        summary_data = []
        for screen in all_screens:
            incoming = incoming_counts.get(screen, 0)
            outgoing = outgoing_counts.get(screen, 0)
            notes = []
            if incoming == 0:
                notes.append("Entry Point")
            if outgoing == 0:
                notes.append("Dead End")
            if any(screen in path for path in issues_df["File Path"].unique()):
                notes.append("Platform Issues ⚠️")
            summary_data.append({
                "Screen Name": screen,
                "Incoming Paths": incoming,
                "Outgoing Paths": outgoing,
                "Notes": ", ".join(notes)
            })
        return pd.DataFrame(summary_data)

    @staticmethod
    def visualize(nav_df, issues_df):
        """Create interactive navigation flow visualization"""
        net = Network(height="750px", width="100%", directed=True)
        nodes = set(nav_df['Source Screen']).union(set(nav_df['Target Screen']))
        problematic_files = issues_df['File Path'].unique()

        for node in nodes:
            color = "red" if any(node in path for path in problematic_files) else "lightblue"
            title = "⚠️ Platform-specific issues detected" if color == "red" else node
            net.add_node(node, label=node, title=title, color=color, size=20)

        for _, row in nav_df.iterrows():
            net.add_edge(row["Source Screen"], row["Target Screen"], 
                        title=row["Action"], label=row["Action"], color="gray")

        net.repulsion(node_distance=150, central_gravity=0.5, damping=0.9)
        net.write_html("navigation_graph.html")
        
        with open("navigation_graph.html", "r", encoding="utf-8") as f:
            html(f.read(), height=750, width=1000)

class Dashboard:
    def __init__(self):
        self.display = DataDisplay()
        self.pattern_guidance = {
            "TabBar": (
                "Use BottomNavigationView for Android. Replace TabBarIOS with a cross-platform navigation library.",
                "https://material.io/components/bottom-navigation"
            ),
            "NavigationController": (
                "Use a Drawer or Stack navigator in React Navigation for Android.",
                "https://reactnavigation.org/"
            ),
            "Modal": (
                "Replace <Modal> with DialogFragment or AlertDialog on Android.",
                "https://developer.android.com/guide/fragments/dialogs"
            )
        }

    def show_comments_overview(self):
        st.header("💬 Comments Overview")
        st.write("Manage all comments across different sections of the dashboard.")

        # Fetch all comments
        comments = CommentManager.get_all_comments()
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            sections = ['All'] + list(set(comment[1] for comment in comments))  # finding_type
            selected_section = st.selectbox('Filter by Section', sections)
        
        with col2:
            sort_options = {
                'Newest First': 'DESC',
                'Oldest First': 'ASC'
            }
            sort_order = st.selectbox('Sort by', list(sort_options.keys()))

        # Filter and sort comments
        filtered_comments = [
            c for c in comments 
            if selected_section == 'All' or c[1] == selected_section
        ]
        
        if sort_options[sort_order] == 'ASC':
            filtered_comments = filtered_comments[::-1]

        # Display comments with edit/delete functionality
        for comment_id, finding_type, finding_id, comment_text, created_at, context_data in filtered_comments:
            with st.expander(f"{finding_type} - {created_at}", expanded=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Section:** {finding_type}")
                    if context_data:
                        st.markdown(f"**Context:** {context_data}")
                    
                    # Edit form
                    with st.form(key=f"edit_form_{comment_id}"):
                        new_comment = st.text_area("Comment", value=comment_text)
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("Save Changes"):
                                success, new_created_at = CommentManager.update_comment(comment_id, new_comment)
                                if success:
                                    st.success("Comment updated successfully!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to update comment.")
                        
                        with col2:
                            if st.form_submit_button("Delete Comment", type="secondary"):
                                if CommentManager.delete_comment(comment_id):
                                    st.success("Comment deleted successfully!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to delete comment.")

    @staticmethod
    def authenticate():
        """Handle user authentication"""
        if "authenticated" not in st.session_state:
            st.session_state["authenticated"] = False

        if not st.session_state["authenticated"]:
            st.title("🔒 Login")
            st.write("Please enter your credentials to access the dashboard.")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if username == USERNAME and password == PASSWORD:
                st.session_state["authenticated"] = True
                st.success("Authentication successful! Please refresh the page.")
                return True
            elif username or password:
                st.error("Invalid credentials")
            return False
        return True

    def show_screens(self):
        self.display.show_dataframe(
            "SELECT * FROM screens",
            ["ID", "Name", "Type", "File Path", "Dependencies", "Created At"],
            "📱 Screens",
            "Screens"
        )

    def show_api_calls(self):
        self.display.show_dataframe(
            "SELECT * FROM api_calls",
            ["ID", "Endpoint", "Method", "Request Body", "Associated Screen ID", "Created At"],
            "🌐 API Calls",
            "API Calls"
        )

    def show_dependencies(self):
        self.display.show_dataframe(
            "SELECT * FROM dependencies",
            ["ID", "Source", "Target", "Type", "File Path", "Created At"],
            "🔗 Dependencies",
            "Dependencies"
        )

    def show_navigation_paths(self):
        st.header("🛠️ Navigation Paths")
        st.write("This visualizes your app's navigation flow. Use it to find screens with missing Android equivalents.")
        
        paths_df = self.display.show_dataframe(
            "SELECT * FROM navigation_paths",
            ["ID", "Source Screen", "Target Screen", "Action", "Created At"],
            None,  # Header already set
            None   # No comments needed for this section
        )
        
        if paths_df is not None:
            issues_df = pd.DataFrame(
                DatabaseManager.execute_query("SELECT file_path FROM platform_issues"),
                columns=["File Path"]
            )
            
            # Show navigation summary
            summary_df = NavigationFlow.analyze_paths(paths_df, issues_df)
            st.write("### Navigation Summary")
            st.dataframe(summary_df.sort_values(
                by=["Incoming Paths", "Outgoing Paths"],
                ascending=[True, False]
            ))

            # Add filters
            st.write("### Filters")
            top_sources = paths_df["Source Screen"].value_counts().head(10).index.tolist()
            selected_source = st.selectbox("Select a Top-Level Source Screen", ["All"] + top_sources)
            max_paths = st.slider("Number of Paths to Display", 10, 200, 50, step=10)

            # Apply filters
            filtered_df = paths_df if selected_source == "All" else paths_df[paths_df["Source Screen"] == selected_source]
            filtered_df = filtered_df.head(max_paths)
            
            st.write(f"Showing {len(filtered_df)} paths")
            st.dataframe(filtered_df)

            if not filtered_df.empty:
                st.subheader("Interactive Navigation Flow")
                NavigationFlow.visualize(filtered_df, issues_df)
                st.write("Red nodes indicate platform-specific issues on that screen.")

    def show_platform_issues(self):
        df = self.display.show_dataframe(
            "SELECT file_path, line_number, issue_type, details, created_at FROM platform_issues",
            ["File Path", "Line Number", "Issue Type", "Details", "Created At"],
            "⚠️ Platform-Specific Issues",
            None,
            "These issues highlight where the app uses iOS-only code or patterns."
        )
        
        if df is not None:
            ios_lib_issues = df[df["Issue Type"] == "ios_library"].copy()
            if not ios_lib_issues.empty:
                st.write("### iOS-Only Libraries and Android Equivalents")
                st.write("Consider replacing these libraries with their Android-friendly counterparts.")
                st.dataframe(ios_lib_issues[["File Path", "Line Number", "Details"]])

    def show_ui_patterns(self):
        df = self.display.show_dataframe(
            "SELECT screen_name, pattern_type, suggested_android, details, created_at FROM ui_patterns",
            ["Screen Name", "Pattern Type", "Suggested Android", "Details", "Created At"],
            "UI Patterns",
            None,
            "iOS-specific UI patterns and their Android equivalents"
        )
        
        if df is not None:
            recommended_actions = []
            docs_links = []
            
            for _, row in df.iterrows():
                p_type = row["Pattern Type"]
                if p_type in self.pattern_guidance:
                    action, docs = self.pattern_guidance[p_type]
                    recommended_actions.append(action)
                    docs_links.append(docs)
                else:
                    recommended_actions.append("No specific guidance available.")
                    docs_links.append("")
                    
            df["Recommended Action"] = recommended_actions
            df["Docs/Links"] = docs_links
            st.dataframe(df)

    def show_device_styling(self):
        self.display.show_dataframe(
            "SELECT file_path, line_number, issue_type, details, created_at FROM device_styling",
            ["File Path", "Line Number", "Issue Type", "Details", "Created At"],
            "Device Styling & Design",
            None,
            "Issues with hardcoded px values and non-material components"
        )

    def show_api_behavior(self):
        self.display.show_dataframe(
            "SELECT api_name, ios_usage, android_considerations, docs_link, created_at FROM api_behavior",
            ["API Name", "iOS Usage", "Android Considerations", "Docs Link", "Created At"],
            "API Behavior Differences",
            None,
            "These APIs behave differently or require extra steps on Android"
        )

    def show_assets(self):
        self.display.show_dataframe(
            "SELECT asset_path, asset_type, ios_variant, android_recommendation, created_at FROM assets",
            ["Asset Path", "Asset Type", "iOS Variant", "Android Recommendation", "Created At"],
            "Assets",
            None,
            "Android uses a drawable-xxxhdpi structure instead of @2x/@3x files"
        )

    def show_testing_coverage(self):
        self.display.show_dataframe(
            "SELECT component_name, test_coverage_percentage, ios_specific_functionality, android_testing_suggestions, created_at FROM testing_coverage",
            ["Component", "Coverage %", "iOS Functionality", "Android Testing Suggestions", "Created At"],
            "Testing Coverage",
            None,
            "Identify components lacking tests or requiring Android-specific tests"
        )

    def show_permissions(self):
        self.display.show_dataframe(
            "SELECT ios_permission, android_permission, notes, created_at FROM permissions_mapping",
            ["iOS Permission", "Android Permission", "Notes", "Created At"],
            "Permissions Mapping",
            None,
            "Map iOS Info.plist permissions to AndroidManifest.xml"
        )

    def show_build_recommendations(self):
        self.display.show_dataframe(
            "SELECT aspect, recommendation, docs_link, created_at FROM build_recommendations",
            ["Aspect", "Recommendation", "Docs Link", "Created At"],
            "Build & Gradle Recommendations",
            None,
            "Set up Gradle, Android Studio, and Android emulators"
        )

    def show_gestures(self):
        self.display.show_dataframe(
            "SELECT ios_gesture, android_equivalent, notes, created_at FROM gestures_mapping",
            ["iOS Gesture", "Android Equivalent", "Notes", "Created At"],
            "Gestures Mapping",
            None,
            "iOS-specific gestures may need to be replaced with Android equivalents"
        )

    def show_native_modules(self):
        self.display.show_dataframe(
            "SELECT ios_module, android_equivalent, bridging_guidance, created_at FROM native_modules",
            ["iOS Module", "Android Equivalent", "Bridging Guidance", "Created At"],
            "Native Modules",
            None,
            "Implement equivalent Java/Kotlin modules for native iOS modules"
        )

    def show_progress_dashboard(self):
        query = """
            SELECT components_ported, ios_libs_replaced, apis_adjusted, 
                   ui_elements_converted, last_updated 
            FROM progress_dashboard 
            ORDER BY last_updated DESC LIMIT 1
        """
        progress_df = self.display.show_dataframe(
            query,
            ["Components Ported", "iOS Libs Replaced", "APIs Adjusted", 
             "UI Elements Converted", "Last Updated"],
            "Porting Progress Dashboard",
            None,
            "Track your progress as you replace iOS libraries and adjust APIs"
        )
        
        if progress_df is not None:
            st.write("Use this as a motivator and checklist reference!")
    
    def show_performance_issues(self):
        self.display.show_dataframe(
            "SELECT file_path, issue_type, details, created_at FROM performance_issues",
            ["File Path", "Issue Type", "Details", "Created At"],
            "Performance Issues",
            None,
            "Identify platform-specific performance bottlenecks"
        )

    def show_hardware_analysis(self):
        self.display.show_dataframe(
            "SELECT file_path, line_number, hardware_type, recommendation, platform_specific FROM hardware_dependencies",
            ["File Path", "Line Number", "Hardware Type", "Recommendation", "Platform Specific"],
            "🔧 Hardware Analysis",
            None,
            "These are the hardware dependencies detected in your project. Ensure compatibility with Android."
        )    

    def show_porting_checklist(self):
        st.header("Porting Checklist (Unified Guidance)")
        st.write("""
        This section aggregates key findings and gives you a prioritized checklist:
        1. Address iOS-only UI patterns (UI Patterns tab) and adopt Material design.
        2. Resolve platform issues (Platform Issues tab) and replace iOS-only libs.
        3. Adjust APIs that differ on Android (API Behavior tab) and set permissions.
        4. Convert assets for Android densities (Assets tab).
        5. Update build processes (Build Recommendations tab).
        6. Improve testing coverage for Android scenarios (Testing Coverage tab).
        7. Check gestures and native modules to ensure Android support.
        8. Track progress in the Progress Dashboard tab.
        9. Fix performance issues and follow recommended docs.
        """)
        st.write("Use the side menu to deep-dive into each category.")

    def run(self):
        """Main dashboard execution"""
        if not self.authenticate():
            return

        st.title("📊 Enhanced React Native App Analysis Dashboard")
        st.write("Welcome! This dashboard analyzes your React Native app for iOS to Android porting.")

        sections = {
            "Porting Checklist": self.show_porting_checklist,
            "Comments Overview": self.show_comments_overview,
            "Screens": self.show_screens,
            "API Calls": self.show_api_calls,
            "Dependencies": self.show_dependencies,
            "Hardware Analysis": self.show_hardware_analysis,
            "Navigation Paths": self.show_navigation_paths,
            "Platform Issues": self.show_platform_issues,
            "UI Patterns": self.show_ui_patterns,
            "Device Styling": self.show_device_styling,
            "API Behavior": self.show_api_behavior,
            "Assets": self.show_assets,
            "Testing Coverage": self.show_testing_coverage,
            "Permissions": self.show_permissions,
            "Build Recommendations": self.show_build_recommendations,
            "Gestures": self.show_gestures,
            "Native Modules": self.show_native_modules,
            "Progress Dashboard": self.show_progress_dashboard,
            "Performance Issues": self.show_performance_issues
        }

        choice = st.sidebar.selectbox("Select a Section", list(sections.keys()))
        sections[choice]()

if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run()