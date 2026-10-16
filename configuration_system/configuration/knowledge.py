import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "knowledge.db"


def get_connection():
    """
    Create a connection to the Knowledge Base.
    """
    return sqlite3.connect(DB_PATH)


def get_all_requirements():
    """
    Return all active requirements.
    DEFAULT is included because it is part of
    the engineering knowledge base.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            requirement_type,
            description
        FROM requirements
        WHERE active = 1
        ORDER BY id
    """)

    rows = cursor.fetchall()

    connection.close()

    requirements = []

    for row in rows:
        requirements.append({
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "description": row[3]
        })

    return requirements


def get_requirement_by_name(requirement_name):
    """
    Find one requirement by its name.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            requirement_type,
            description
        FROM requirements
        WHERE name = ?
          AND active = 1
    """, (requirement_name,))

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "type": row[2],
        "description": row[3]
    }


def get_parameters_for_requirement(requirement_name):
    """
    Return all parameters associated with a requirement,
    including their PLC/PC mappings.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            p.id,
            p.name,
            p.data_type,
            p.description,
            pm.access_type,
            pm.plc_parameter_name,
            pm.pc_parameter_name

        FROM requirements r

        JOIN requirement_parameters rp
            ON r.id = rp.requirement_id

        JOIN parameters p
            ON p.id = rp.parameter_id

        LEFT JOIN parameter_mappings pm
            ON pm.parameter_id = p.id

        WHERE r.name = ?

        ORDER BY p.id, pm.id
    """, (requirement_name,))

    rows = cursor.fetchall()

    connection.close()

    parameters = []

    for row in rows:
        parameters.append({
            "id": row[0],
            "name": row[1],
            "data_type": row[2],
            "description": row[3],
            "access_type": row[4],
            "plc_parameter_name": row[5],
            "pc_parameter_name": row[6]
        })

    return parameters


def get_parameters_for_requirements(requirement_names):
    """
    Return all parameters for multiple requirements.

    DEFAULT is automatically included.
    """

    selected_names = list(requirement_names)

    if "DEFAULT" not in selected_names:
        selected_names.insert(0, "DEFAULT")

    all_parameters = {}

    for requirement_name in selected_names:

        parameters = get_parameters_for_requirement(
            requirement_name
        )

        for parameter in parameters:

            parameter_id = parameter["id"]

            if parameter_id not in all_parameters:

                all_parameters[parameter_id] = {
                    "id": parameter["id"],
                    "name": parameter["name"],
                    "data_type": parameter["data_type"],
                    "description": parameter["description"],
                    "requirements": [],
                    "mappings": []
                }

            # Record which requirement uses this parameter
            if requirement_name not in all_parameters[parameter_id]["requirements"]:
                all_parameters[parameter_id]["requirements"].append(
                    requirement_name
                )

            # Add mapping if one exists
            mapping = {
                "access_type": parameter["access_type"],
                "plc_parameter_name": parameter["plc_parameter_name"],
                "pc_parameter_name": parameter["pc_parameter_name"]
            }

            if mapping not in all_parameters[parameter_id]["mappings"]:
                all_parameters[parameter_id]["mappings"].append(mapping)

    return list(all_parameters.values())