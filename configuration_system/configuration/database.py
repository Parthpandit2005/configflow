import sqlite3
from pathlib import Path


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "knowledge.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return a connection to the Knowledge Base.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    # Enable foreign key relationships
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    connection = get_connection()
    cursor = connection.cursor()

    # ========================================================
    # REQUIREMENTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requirements (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL UNIQUE,

            requirement_type TEXT NOT NULL DEFAULT 'SELECTABLE',

            description TEXT,

            active INTEGER NOT NULL DEFAULT 1,

            CHECK (
                requirement_type IN (
                    'DEFAULT',
                    'SELECTABLE'
                )
            ),

            CHECK (
                active IN (0, 1)
            )
        )
    """)


    # ========================================================
    # PARAMETERS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parameters (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL UNIQUE,

            data_type TEXT,

            description TEXT,

            CHECK (
                data_type IS NULL OR
                data_type IN (
                    'Integer',
                    'Real',
                    'Boolean',
                    'String'
                )
            )
        )
    """)


    # ========================================================
    # PARAMETER MAPPINGS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parameter_mappings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            parameter_id INTEGER NOT NULL,

            plc_parameter_name TEXT,

            pc_parameter_name TEXT,

            access_type TEXT NOT NULL,

            description TEXT,

            FOREIGN KEY (parameter_id)
                REFERENCES parameters(id)
                ON DELETE CASCADE,

            CHECK (
                access_type IN (
                    'ReadOnly',
                    'WriteOnly',
                    'ReadWrite'
                )
            ),

            UNIQUE (
                parameter_id,
                plc_parameter_name,
                pc_parameter_name,
                access_type
            )
        )
    """)


    # ========================================================
    # REQUIREMENT → PARAMETER
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requirement_parameters (

            requirement_id INTEGER NOT NULL,

            parameter_id INTEGER NOT NULL,

            PRIMARY KEY (
                requirement_id,
                parameter_id
            ),

            FOREIGN KEY (requirement_id)
                REFERENCES requirements(id)
                ON DELETE CASCADE,

            FOREIGN KEY (parameter_id)
                REFERENCES parameters(id)
                ON DELETE CASCADE
        )
    """)


    # ========================================================
    # PROJECTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL UNIQUE,

            customer TEXT,

            project_number TEXT,

            description TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # ========================================================
    # PROJECT → REQUIREMENT
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_requirements (

            project_id INTEGER NOT NULL,

            requirement_id INTEGER NOT NULL,

            PRIMARY KEY (
                project_id,
                requirement_id
            ),

            FOREIGN KEY (project_id)
                REFERENCES projects(id)
                ON DELETE CASCADE,

            FOREIGN KEY (requirement_id)
                REFERENCES requirements(id)
                ON DELETE CASCADE
        )
    """)


    # ========================================================
    # PROJECT → ACTUAL PARAMETERS
    #
    # This is useful later when we record the actual
    # configuration used by a historical project.
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_parameters (

            project_id INTEGER NOT NULL,

            parameter_id INTEGER NOT NULL,

            PRIMARY KEY (
                project_id,
                parameter_id
            ),

            FOREIGN KEY (project_id)
                REFERENCES projects(id)
                ON DELETE CASCADE,

            FOREIGN KEY (parameter_id)
                REFERENCES parameters(id)
                ON DELETE CASCADE
        )
    """)


    # ========================================================
    # INDEXES
    # ========================================================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_requirement_parameters_requirement
        ON requirement_parameters(requirement_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_requirement_parameters_parameter
        ON requirement_parameters(parameter_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_parameter_mappings_parameter
        ON parameter_mappings(parameter_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_project_requirements_project
        ON project_requirements(project_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_project_requirements_requirement
        ON project_requirements(requirement_id)
    """)


    # ========================================================
    # SAVE
    # ========================================================

    connection.commit()
    connection.close()

    print("=" * 60)
    print("KNOWLEDGE DATABASE CREATED")
    print("=" * 60)
    print()
    print("Database:")
    print(DB_PATH)
    print()
    print("Tables created:")
    print("  - requirements")
    print("  - parameters")
    print("  - parameter_mappings")
    print("  - requirement_parameters")
    print("  - projects")
    print("  - project_requirements")
    print("  - project_parameters")
    print()


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":
    create_database()