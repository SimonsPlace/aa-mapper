# src/db/database.py
import os
import logging
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Database:
    """
    Database class to manage PostgreSQL interactions.
    """
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
            self.cursor = self.connection.cursor()
            logging.info("Database connection established successfully.")
        except Exception as e:
            logging.error(f"Error connecting to database: {e}")
            raise e

    def insert_screens(self, screens):
        for screen in screens:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO screens (name, type, file_path, dependencies, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (name, file_path) DO NOTHING
                    """,
                    (screen["name"], screen["type"], screen["file_path"], screen.get("dependencies"))
                )
            except Exception as e:
                logging.error(f"Error inserting screen: {screen}, Error: {e}")
        self.connection.commit()

    def insert_api_calls(self, api_calls):
        for call in api_calls:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO api_calls (endpoint, method, request_body, associated_screen_id, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (endpoint, method) DO NOTHING
                    """,
                    (call["endpoint"], call["method"], call.get("request_body"), call.get("associated_screen_id"))
                )
            except Exception as e:
                logging.error(f"Error inserting api call: {call}, Error: {e}")
        self.connection.commit()

    def insert_dependencies(self, dependencies):
        for dep in dependencies:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO dependencies (source, target, type, file_path, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (source, target, type) DO NOTHING
                    """,
                    (dep["source"], dep["target"], dep["type"], dep.get("file_path"))
                )
            except Exception as e:
                logging.error(f"Error inserting dependency: {dep}, Error: {e}")
        self.connection.commit()

    def insert_platform_issues(self, platform_issues):
        for issue in platform_issues:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO platform_issues (file_path, line_number, issue_type, details, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT (file_path, line_number, issue_type, details) DO NOTHING
                    """,
                    (issue["file_path"], issue["line_number"], issue["issue_type"], issue["details"])
                )
            except Exception as e:
                logging.error(f"Error inserting platform issue: {issue}, Error: {e}")
        self.connection.commit()

    def insert_navigation_paths(self, navigation_edges):
        for edge in navigation_edges:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO navigation_paths (source_screen, target_screen, action, created_at)
                    VALUES (%s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    (edge["source"], edge["target"], edge["action"])
                )
            except Exception as e:
                logging.error(f"Error inserting navigation path: {edge}, Error: {e}")
        self.connection.commit()

    def insert_ui_patterns(self, ui_patterns):
        for item in ui_patterns:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO ui_patterns (screen_name, pattern_type, suggested_android, details, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    (item["screen_name"], item["pattern_type"], item["suggested_android"], item["details"])
                )
            except Exception as e:
                logging.error(f"Error inserting ui_pattern: {item}, Error: {e}")
        self.connection.commit()

    def insert_device_styling(self, device_styling_issues):
        for item in device_styling_issues:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO device_styling (file_path, line_number, issue_type, details, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    (item["file_path"], item["line_number"], item["issue_type"], item["details"])
                )
            except Exception as e:
                logging.error(f"Error inserting device styling issue: {item}, Error: {e}")
        self.connection.commit()

    def insert_api_behavior(self, api_behavior_diffs):
        for item in api_behavior_diffs:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO api_behavior (api_name, ios_usage, android_considerations, docs_link, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        item["api_name"],
                        item.get("ios_usage",""),
                        item.get("android_considerations",""),
                        item.get("docs_link","")
                    )
                )
            except Exception as e:
                logging.error(f"Error inserting api behavior: {item}, Error: {e}")
        self.connection.commit()

    def insert_assets(self, asset_list):
        for asset in asset_list:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO assets (asset_path, asset_type, ios_variant, android_recommendation, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        asset["asset_path"],
                        asset["asset_type"],
                        asset.get("ios_variant",""),
                        asset.get("android_recommendation","")
                    )
                )
            except Exception as e:
                logging.error(f"Error inserting asset: {asset}, Error: {e}")
        self.connection.commit()

    def insert_testing_coverage(self, testing_gaps):
        for gap in testing_gaps:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO testing_coverage (component_name, test_coverage_percentage, ios_specific_functionality, android_testing_suggestions, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        gap["component_name"],
                        gap.get("test_coverage_percentage",0.0),
                        gap.get("ios_specific_functionality",""),
                        gap.get("android_testing_suggestions","")
                    )
                )
            except Exception as e:
                logging.error(f"Error inserting testing coverage: {gap}, Error: {e}")
        self.connection.commit()

    def insert_permissions_mapping(self, permission_map):
        for p in permission_map:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO permissions_mapping (ios_permission, android_permission, notes, created_at)
                    VALUES (%s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        p["ios_permission"],
                        p.get("android_permission",""),
                        p.get("notes","")
                    )
                )
            except Exception as e:
                logging.error(f"Error inserting permission mapping: {p}, Error: {e}")
        self.connection.commit()

    def insert_build_recommendations(self, build_recos):
        for rec in build_recos:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO build_recommendations (aspect, recommendation, docs_link, created_at)
                    VALUES (%s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        rec["aspect"],
                        rec["recommendation"],
                        rec.get("docs_link","")
                    )
                )
            except Exception as e:
                logging.error(f"Error inserting build recommendation: {rec}, Error: {e}")
        self.connection.commit()

    def insert_gestures_mapping(self, gestures):
        for g in gestures:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO gestures_mapping (ios_gesture, android_equivalent, notes, docs_link, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        g["ios_gesture"],
                        g.get("android_equivalent",""),
                        g.get("notes",""),
                        g.get("docs_link","")
                    )
                )
            except Exception as e:
                logging.error(f"Error inserting gesture mapping: {g}, Error: {e}")
        self.connection.commit()

    def insert_native_modules(self, native_modules):
        for nm in native_modules:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO native_modules (ios_module, android_equivalent, bridging_guidance, docs_link, created_at)
                    VALUES (%s, %s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        nm["ios_module"],
                        nm.get("android_equivalent",""),
                        nm.get("bridging_guidance",""),
                        nm.get("docs_link","")
                    )
                )
            except Exception as e:
                logging.error(f"Error inserting native module: {nm}, Error: {e}")
        self.connection.commit()

    def insert_progress_dashboard(self, progress_data):
        try:
            self.cursor.execute(
                """
                INSERT INTO progress_dashboard (components_ported, ios_libs_replaced, apis_adjusted, ui_elements_converted, last_updated)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT DO NOTHING
                """,
                (
                    progress_data.get("components_ported",0),
                    progress_data.get("ios_libs_replaced",0),
                    progress_data.get("apis_adjusted",0),
                    progress_data.get("ui_elements_converted",0)
                )
            )
        except Exception as e:
            logging.error(f"Error inserting progress dashboard: {progress_data}, Error: {e}")
        self.connection.commit()

    def insert_performance_issues(self, perf_issues):
        for pi in perf_issues:
            try:
                self.cursor.execute(
                    """
                    INSERT INTO performance_issues (file_path, issue_type, details, docs_link, recommendation, created_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        pi["file_path"],
                        pi["issue_type"],
                        pi["details"],
                        pi.get("docs_link",""),
                        pi.get("recommendation","")
                    )
                )
            except Exception as e:
                logging.error(f"Error inserting performance issue: {pi}, Error: {e}")
        self.connection.commit()

    def close(self):
        try:
            self.cursor.close()
            self.connection.close()
            logging.info("Database connection closed.")
        except Exception as e:
            logging.error(f"Error closing database connection: {e}")

    def get_connection(self):
        return self.connection

def get_db_connection():
    """
    Returns a raw database connection. This function is used by the dashboard for read-only queries.
    """
    db = Database()
    return db.get_connection()
