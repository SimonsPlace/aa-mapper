import argparse
from src.db.database import get_db_connection
from src.dashboard.app_dashboard import launch_dashboard
from analyze_app import analyze_app

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="React Native App Analysis Tool")
    parser.add_argument("--project-path", required=True, help="Path to the React Native project.")
    parser.add_argument("--dashboard", action="store_true", help="Launch the analysis dashboard.")
    args = parser.parse_args()

    if args.dashboard:
        # Launch the Streamlit dashboard
        launch_dashboard()
    else:
        # Run the analysis
        analyze_app(args.project_path)

if __name__ == "__main__":
    main()
