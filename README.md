React Native iOS-to-Android Porting Analysis Tool
This tool analyzes a React Native project that was originally developed for iOS and provides guidance, metrics, and suggestions for porting it to Android. It scans your codebase to identify platform-specific issues, UI patterns, API behaviors, dependencies, permissions, and more. It then stores these findings in a PostgreSQL database and provides a Streamlit-powered dashboard to visualize and track your porting progress.

Key Features
Screens & Navigation Paths: Identify all screens and visualize app navigation flow.
UI Patterns: Detect iOS-specific UI components (e.g., TabBarIOS, <Modal>) and suggest Android equivalents.
API Behavior Differences: Highlight APIs that behave differently on Android and provide links to documentation.
Platform-Specific Code & Libraries: Flag iOS-only libraries and offer Android-friendly alternatives.
Assets & Styling: Show asset usage and styling issues (e.g., hardcoded px) and suggest Android best practices (dp, sp, Material components).
Permissions Mapping: Map iOS (Info.plist) permissions to Android (AndroidManifest.xml) equivalents.
Build Recommendations: Suggest Gradle configs, emulator setup, and other Android build environment configurations.
Testing Coverage & Native Modules: Identify testing gaps for Android-specific scenarios and guide on rewriting native iOS modules in Java/Kotlin.
Progress Dashboard: Track how many components you’ve ported, how many APIs adjusted, etc.
Performance Issues: Spot potential performance bottlenecks and offer optimization strategies.
System Requirements
Python: 3.8 or later recommended.
PostgreSQL: A running PostgreSQL instance with valid credentials and access.
Node.js & React Native dependencies: The target React Native project's dependencies should be installed.
Streamlit: Installed in your Python environment to run the dashboard.
Installation & Setup
Clone the Repository:

bash
Copy code
git clone https://github.com/simonsplace/aa-mapper.git
cd aa-mapper
Set Up Python Environment (recommended):

bash
Copy code
python3 -m venv venv
source venv/bin/activate
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Configure Environment Variables:

Create a .env file in the project root.
Set your DB credentials (and any other necessary vars):
env
Copy code
DB_NAME=your_db_name
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
Set Up the Database Schema:

Ensure your PostgreSQL instance is running.
Run the provided SQL schema script to create tables:
bash
Copy code
psql -h localhost -U your_user -d your_db_name -f schema.sql
Adjust host/user/db_name as needed.

Running the Analysis
Point the Analyzer to Your Project:

Suppose your React Native project is located at ~/Downloads/your-react-native-app.
Run the Analyzer:

bash
Copy code
python analyze_app.py --project-path ~/Downloads/your-react-native-app
This will parse the project, populate the database, and log analysis steps in analysis.log.
Check Logs:

If needed, view analysis.log for details:
bash
Copy code
cat analysis.log
Viewing the Dashboard
Start the Dashboard:

bash
Copy code
streamlit run src/dashboard/app_dashboard.py
Open in Browser:

The terminal will show a local URL (typically http://localhost:8501).
Open that URL in your web browser to explore the analysis results.
Interpreting Results
Porting Checklist: Start here for a high-level overview of what needs to be done.
Screens & Navigation: Understand your app’s architecture and identify screens that may need special attention.
UI Patterns & Platform Issues: Quickly spot iOS-only features and read recommendations on converting them to Android equivalents.
API Behavior, Permissions, and Build Recommendations: Plan your Android integration steps—adjust code for different APIs, add necessary Android permissions, and follow build suggestions.
Testing & Performance: Identify where more tests are needed for Android scenarios and where to optimize performance.
Customizing & Extending
Custom Rules: Add more patterns or custom iOS-to-Android mappings in src/parser/enhanced_analyzers.py.
Database Schema Updates: Modify schema.sql if you want to store additional data points.
Dashboard Enhancements: Tweak app_dashboard.py to add more charts, filters, or summaries.
Troubleshooting
No Output/Empty Results: Check analysis.log for errors. Make sure the path to your project is correct and that you have read permissions.
Database Errors: Confirm that your DB credentials are correct and that you’ve applied the schema.
Missing Features: Ensure you’ve run pip install -r requirements.txt and that all Python packages are up-to-date.
Contributing
Contributions, bug reports, and feature requests are welcome. Please open issues or pull requests on the repository’s GitHub page.

License
This project is released under the MIT License. See LICENSE for details.