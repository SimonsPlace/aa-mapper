-- Screens Table
CREATE TABLE IF NOT EXISTS screens (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,                -- Screen name
    type TEXT,                         -- Type of screen (e.g., functional, class-based, modal)
    file_path TEXT NOT NULL,           -- Full file path to the screen
    dependencies TEXT,                 -- Comma-separated list of dependencies (e.g., React, Redux)
    created_at TIMESTAMP DEFAULT NOW() -- Timestamp when the record was created
);

-- API Calls Table
CREATE TABLE IF NOT EXISTS api_calls (
    id SERIAL PRIMARY KEY,
    endpoint TEXT NOT NULL,            -- API endpoint URL
    method TEXT NOT NULL,              -- HTTP method (e.g., GET, POST)
    request_body TEXT,                 -- Example or template request body
    associated_screen_id INT,          -- Foreign key linking to the screens table
    created_at TIMESTAMP DEFAULT NOW(),-- Timestamp when the record was created
    FOREIGN KEY (associated_screen_id) REFERENCES screens (id) ON DELETE SET NULL
);

-- Dependencies Table
CREATE TABLE IF NOT EXISTS dependencies (
    id SERIAL PRIMARY KEY,
    source TEXT NOT NULL,              -- Source file that contains the import
    target TEXT NOT NULL,              -- Imported file/module
    type TEXT NOT NULL,                -- Dependency type (e.g., import, require, dynamic)
    file_path TEXT,                    -- Full file path of the source file (optional for additional context)
    created_at TIMESTAMP DEFAULT NOW() -- Timestamp when the record was created
);

-- Navigation Paths Table
CREATE TABLE IF NOT EXISTS navigation_paths (
    id SERIAL PRIMARY KEY,
    source_screen TEXT NOT NULL,       -- Source screen name
    target_screen TEXT NOT NULL,       -- Target screen name
    action TEXT NOT NULL,              -- Navigation action (e.g., navigate, push)
    created_at TIMESTAMP DEFAULT NOW() -- Timestamp when the record was created
);

-- Platform Issues Table
CREATE TABLE IF NOT EXISTS platform_issues (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,           -- File path where the issue was found
    line_number INT NOT NULL,          -- Line number of the issue
    issue_type TEXT NOT NULL,          -- "platform_code" or "ios_library"
    details TEXT NOT NULL,             -- Code snippet or library name causing the issue
    created_at TIMESTAMP DEFAULT NOW(),-- Timestamp when the record was created
    CONSTRAINT unique_platform_issue UNIQUE (file_path, line_number, issue_type, details)
);

CREATE TABLE IF NOT EXISTS ui_patterns (
    id SERIAL PRIMARY KEY,
    screen_name TEXT,
    pattern_type TEXT,
    suggested_android TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS device_styling (
    id SERIAL PRIMARY KEY,
    file_path TEXT,
    line_number INT,
    issue_type TEXT,
    details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS api_behavior (
    id SERIAL PRIMARY KEY,
    api_name TEXT,
    ios_usage TEXT,
    android_considerations TEXT,
    docs_link TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    asset_path TEXT,
    asset_type TEXT,
    ios_variant TEXT,
    android_recommendation TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS testing_coverage (
    id SERIAL PRIMARY KEY,
    component_name TEXT,
    test_coverage_percentage REAL,
    ios_specific_functionality TEXT,
    android_testing_suggestions TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS permissions_mapping (
    id SERIAL PRIMARY KEY,
    ios_permission TEXT,
    android_permission TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS build_recommendations (
    id SERIAL PRIMARY KEY,
    aspect TEXT,
    recommendation TEXT,
    docs_link TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS gestures_mapping (
    id SERIAL PRIMARY KEY,
    ios_gesture TEXT,
    android_equivalent TEXT,
    notes TEXT,
    docs_link TEXT,            -- New field for docs
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS native_modules (
    id SERIAL PRIMARY KEY,
    ios_module TEXT,
    android_equivalent TEXT,
    bridging_guidance TEXT,
    docs_link TEXT,            -- New field for docs
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS progress_dashboard (
    id SERIAL PRIMARY KEY,
    components_ported INT,
    ios_libs_replaced INT,
    apis_adjusted INT,
    ui_elements_converted INT,
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS performance_issues (
    id SERIAL PRIMARY KEY,
    file_path TEXT,
    issue_type TEXT,
    details TEXT,
    docs_link TEXT,            -- New field for docs
    recommendation TEXT,       -- New field for recommendation
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE hardware_dependencies (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    line_number INT NOT NULL,
    hardware_type TEXT NOT NULL,
    recommendation TEXT,
    platform_specific TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_hardware_dependency UNIQUE (file_path, line_number, hardware_type)
);

-- Indexes for faster lookups
CREATE UNIQUE INDEX IF NOT EXISTS idx_screens_unique ON screens (name, file_path);
CREATE UNIQUE INDEX IF NOT EXISTS idx_api_calls_unique ON api_calls (endpoint, method);
CREATE UNIQUE INDEX IF NOT EXISTS idx_dependencies_unique ON dependencies (source, target, type);
CREATE UNIQUE INDEX IF NOT EXISTS idx_platform_issues_unique ON platform_issues (file_path, line_number, issue_type, details);
