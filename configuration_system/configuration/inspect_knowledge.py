import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "knowledge.db"


def inspect_knowledge():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    print("=" * 70)
    print("KNOWLEDGE BASE INSPECTION")
    print("=" * 70)

    # ------------------------------------------------------------
    # REQUIREMENTS
    # ------------------------------------------------------------

    print("\nREQUIREMENTS")
    print("-" * 70)

    cursor.execute("""
        SELECT id, name, requirement_type, active
        FROM requirements
        ORDER BY id
    """)

    requirements = cursor.fetchall()

    for requirement in requirements:
        print(
            f"ID={requirement[0]:<3} "
            f"{requirement[1]:<30} "
            f"type={requirement[2]:<10} "
            f"active={requirement[3]}"
        )

    # ------------------------------------------------------------
    # PARAMETER COUNT PER REQUIREMENT
    # ------------------------------------------------------------

    print("\nPARAMETERS PER REQUIREMENT")
    print("-" * 70)

    cursor.execute("""
        SELECT
            r.name,
            COUNT(rp.parameter_id)
        FROM requirements r
        LEFT JOIN requirement_parameters rp
            ON r.id = rp.requirement_id
        GROUP BY r.id, r.name
        ORDER BY r.id
    """)

    counts = cursor.fetchall()

    for requirement_name, parameter_count in counts:
        print(
            f"{requirement_name:<35} "
            f"{parameter_count} parameters"
        )

    # ------------------------------------------------------------
    # PARAMETER / MAPPING SAMPLE
    # ------------------------------------------------------------

    print("\nPARAMETER MAPPINGS")
    print("-" * 70)

    cursor.execute("""
        SELECT
            r.name,
            p.name,
            p.data_type,
            pm.access_type,
            pm.plc_parameter_name,
            pm.pc_parameter_name
        FROM requirement_parameters rp

        JOIN requirements r
            ON r.id = rp.requirement_id

        JOIN parameters p
            ON p.id = rp.parameter_id

        LEFT JOIN parameter_mappings pm
            ON pm.parameter_id = p.id

        ORDER BY r.id, p.id
        LIMIT 30
    """)

    mappings = cursor.fetchall()

    for row in mappings:
        requirement = row[0]
        parameter = row[1]
        data_type = row[2] or "NULL"
        access = row[3] or "NULL"
        plc = row[4] or "NULL"
        pc = row[5] or "NULL"

        print(f"\nRequirement : {requirement}")
        print(f"Parameter   : {parameter}")
        print(f"Data Type   : {data_type}")
        print(f"Access      : {access}")
        print(f"PLC         : {plc}")
        print(f"PC          : {pc}")

    # ------------------------------------------------------------
    # TOTALS
    # ------------------------------------------------------------

    print("\nDATABASE TOTALS")
    print("-" * 70)

    tables = [
        "requirements",
        "parameters",
        "parameter_mappings",
        "requirement_parameters",
        "projects",
        "project_requirements",
        "project_parameters",
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]

        print(f"{table:<25} {count}")

    connection.close()

    print("\n" + "=" * 70)
    print("INSPECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    inspect_knowledge()