import sys
import os
import argparse
import logging
from dotenv import load_dotenv

# Ensure the root directory is in the path for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.database import Database
from src.parser.hardware_analyzer import HardwareAnalyzer

# Existing parsers
from src.parser.js_parser import parse_screens
from src.parser.api_parser import parse_api_calls
from src.parser.dependency_analyzer import parse_dependencies
from src.parser.platform_analyzer import analyze_platform_specific_code

# Enhanced analyzers for new features
from src.parser.enhanced_analyzers import (
    analyze_ui_patterns,
    analyze_device_styling,
    analyze_api_behavior,
    analyze_assets,
    analyze_testing_coverage,
    analyze_permissions,
    analyze_build_recommendations,
    analyze_gestures_and_native_modules,
    analyze_progress,
    analyze_performance_issues
)

load_dotenv()

log_file = "analysis.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def analyze_app(project_path):
    logging.info("Starting enhanced analysis of the app...")
    logging.debug(f"Project path: {project_path}")

    # Check if project path is a directory and accessible
    if not os.path.exists(project_path):
        logging.error(f"Project path does not exist: {project_path}")
        return

    # Attempt DB connection
    logging.info("Attempting database connection...")
    try:
        db = Database()
    except Exception as e:
        logging.error("Failed to establish database connection", exc_info=True)
        return
    logging.info("Database connection established.")

    try:
        logging.info("Parsing screens and navigation edges...")
        screens, navigation_edges = parse_screens(project_path)
        logging.debug(f"Screens found: {len(screens)}, Navigation paths found: {len(navigation_edges)}")

        logging.info("Parsing API calls...")
        api_calls = parse_api_calls(project_path)
        logging.debug(f"API calls found: {len(api_calls)}")

        logging.info("Parsing dependencies...")
        dependencies = parse_dependencies(project_path)
        logging.debug(f"Dependencies found: {len(dependencies)}")

        logging.info("Analyzing platform-specific code...")
        platform_issues = analyze_platform_specific_code(project_path)
        logging.debug(f"Platform issues found: {len(platform_issues)}")

        # Enhanced analysis
        logging.info("Analyzing UI patterns...")
        ui_patterns = analyze_ui_patterns(project_path)
        logging.debug(f"UI patterns found: {len(ui_patterns)}")

        logging.info("Analyzing device styling...")
        device_styling_issues = analyze_device_styling(project_path)
        logging.debug(f"Device styling issues found: {len(device_styling_issues)}")

        logging.info("Analyzing API behavior differences...")
        api_behavior_diffs = analyze_api_behavior(project_path)
        logging.debug(f"API behavior diffs found: {len(api_behavior_diffs)}")

        logging.info("Analyzing assets...")
        asset_list = analyze_assets(project_path)
        logging.debug(f"Assets found: {len(asset_list)}")

        logging.info("Analyzing testing coverage...")
        testing_gaps = analyze_testing_coverage(project_path)
        logging.debug(f"Testing coverage gaps found: {len(testing_gaps)}")

        logging.info("Analyzing permissions mapping...")
        permission_map = analyze_permissions(project_path)
        logging.debug(f"Permissions mapped: {len(permission_map)}")

        logging.info("Analyzing build recommendations...")
        build_recos = analyze_build_recommendations(project_path)
        logging.debug(f"Build recommendations: {len(build_recos)}")

        logging.info("Analyzing gestures and native modules...")
        gestures_and_modules = analyze_gestures_and_native_modules(project_path)
        logging.debug("Gestures: %d, Native modules: %d", 
                      len(gestures_and_modules.get("gestures", [])), 
                      len(gestures_and_modules.get("native_modules", [])))

        logging.info("Analyzing porting progress...")
        progress_data = analyze_progress(project_path)
        logging.debug(f"Progress data: {progress_data}")

        logging.info("Analyzing performance issues...")
        perf_issues = analyze_performance_issues(project_path)
        logging.debug(f"Performance issues: {len(perf_issues)}")

        logging.info("Analyzing hardware dependencies...")
        analyzer = HardwareAnalyzer()
        hardware_issues = analyzer.analyze(project_path)
        logging.debug(f"Hardware issues found: {len(hardware_issues)}")

        # Save results to DB
        logging.info("Inserting screens...")
        db.insert_screens(screens)

        logging.info("Inserting API calls...")
        db.insert_api_calls(api_calls)

        logging.info("Inserting dependencies...")
        db.insert_dependencies(dependencies)

        logging.info("Inserting platform issues...")
        db.insert_platform_issues(platform_issues)

        logging.info("Inserting navigation paths...")
        db.insert_navigation_paths(navigation_edges)

        logging.info("Inserting UI patterns...")
        db.insert_ui_patterns(ui_patterns)

        logging.info("Inserting device styling issues...")
        db.insert_device_styling(device_styling_issues)

        logging.info("Inserting API behavior differences...")
        db.insert_api_behavior(api_behavior_diffs)

        logging.info("Inserting assets...")
        db.insert_assets(asset_list)

        logging.info("Inserting testing coverage info...")
        db.insert_testing_coverage(testing_gaps)

        logging.info("Inserting permissions mapping...")
        db.insert_permissions_mapping(permission_map)

        logging.info("Inserting build recommendations...")
        db.insert_build_recommendations(build_recos)

        if gestures_and_modules:
            logging.info("Inserting gestures mapping...")
            db.insert_gestures_mapping(gestures_and_modules.get("gestures", []))

            logging.info("Inserting native modules mapping...")
            db.insert_native_modules(gestures_and_modules.get("native_modules", []))

        logging.info("Inserting progress dashboard data...")
        db.insert_progress_dashboard(progress_data)

        logging.info("Inserting performance issues...")
        db.insert_performance_issues(perf_issues)

        logging.info("Inserting hardware dependencies...")
        db.insert_hardware_dependencies(hardware_issues)

        logging.info("Analysis complete! View the results in the dashboard.")
    except Exception as e:
        logging.error(f"An error occurred during analysis: {e}", exc_info=True)
    finally:
        db.close()
        logging.info("Database connection closed.")

if __name__ == "__main__":
    print("Starting analysis...")
    parser = argparse.ArgumentParser(description="Analyze a React Native project with enhanced features.")
    parser.add_argument("--project-path", required=True, help="Path to the React Native project.")
    args = parser.parse_args()

    project_path = args.project_path
    analyze_app(project_path)
    print("Analysis triggered, check logs for progress.")
