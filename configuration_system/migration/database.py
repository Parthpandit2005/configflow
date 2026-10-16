import pyodbc
import pandas as pd
import xml.etree.ElementTree as ET

def connect_webpro(
    server,
    database,
    username=None,
    password=None,
    auth_mode="Windows Authentication"
):

    import os

    database_name = database

    if auth_mode == "Windows Authentication":

        connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={server};"
            f"DATABASE={database_name};"
            "Trusted_Connection=yes;"
        )

    else:

        connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={server};"
            f"DATABASE={database_name};"
            f"UID={username};"
            f"PWD={password};"
        )
    return pyodbc.connect(connection_string)

def get_webpro_models(connection):

    query = """
    SELECT
        ID,
        VehicleModelName
    FROM dbo.tbl_MASTER_VEHICLEMODEL_NAME
    """

    webpro_models = pd.read_sql(
        query,
        connection
    )

    return webpro_models

def get_project_plc_configuration(connection):
    """
    Find the project's PLC in DeviceMaster.

    PLC condition:
        CategoryID = 16
        Attached = True
    """

    query = """
    SELECT TOP 1000
        ID,
        CategoryID,
        Model,
        Attached,
        Configuration
    FROM dbo.DeviceMaster
    WHERE CategoryID = 16
      AND Attached = 1
    """

    plc_devices = pd.read_sql(query, connection)

    if plc_devices.empty:
        raise ValueError(
            "No PLC device found in DeviceMaster "
            "(CategoryID=16 and Attached=True)."
        )

    if len(plc_devices) > 1:
        raise ValueError(
            f"Multiple attached PLC devices found: {len(plc_devices)}"
        )

    plc = plc_devices.iloc[0]

    return {
        "device_id": plc["ID"],
        "model": plc["Model"],
        "configuration": plc["Configuration"]
    }


def extract_parameter_ids(configuration_xml):
    """
    Extract all ParameterID values from the PLC configuration XML.
    """

    if configuration_xml is None:
        raise ValueError("PLC Configuration XML is empty.")

    root = ET.fromstring(str(configuration_xml))

    parameter_ids = set()

    for element in root.iter("ParameterID"):
        if element.text:
            parameter_id = element.text.strip()

            if parameter_id:
                parameter_ids.add(parameter_id)

    return parameter_ids


def get_parameter_master(connection):
    """
    Get all required parameter information from ParameterMaster.
    Comment and Configuration are intentionally excluded.
    """

    query = """
    SELECT
        ID,
        ParameterType,
        DeviceID,
        Name,
        DisplayName,
        Category,
        InterfacedVia,
        ValueType,
        IsAttached,
        IsSystemParameter
    FROM dbo.ParameterMaster
    """

    return pd.read_sql(query, connection)


def compare_project_parameters(connection):
    """
    Complete project parameter analysis.

    1. Find project PLC
    2. Extract its configuration XML
    3. Extract ParameterIDs
    4. Compare against ParameterMaster
    """

    plc = get_project_plc_configuration(connection)

    xml_parameter_ids = extract_parameter_ids(
        plc["configuration"]
    )

    parameter_master = get_parameter_master(connection)

    parameter_master["ID"] = (
        parameter_master["ID"]
        .astype(str)
        .str.strip()
    )

    used = parameter_master[
        parameter_master["ID"].isin(xml_parameter_ids)
    ].copy()

    unused = parameter_master[
        ~parameter_master["ID"].isin(xml_parameter_ids)
    ].copy()

    return {
        "plc_model": plc["model"],
        "plc_device_id": plc["device_id"],
        "xml_parameter_ids": xml_parameter_ids,
        "parameter_master": parameter_master,
        "used_parameters": used,
        "unused_parameters": unused
    }

def build_project_parameter_mapping(connection):
    """
    Build the project parameter mapping for Excel export.

    Output columns:
        Data Type
        Access
        PLC Parameter
        PC Parameter
    """

    plc = get_project_plc_configuration(connection)

    configuration_xml = plc["configuration"]

    if configuration_xml is None:
        raise ValueError("PLC Configuration XML is empty.")

    root = ET.fromstring(str(configuration_xml))

    # ---------------------------------------------------------
    # Get ParameterMaster
    # ---------------------------------------------------------
    parameter_master = get_parameter_master(connection)

    parameter_master["ID"] = (
        parameter_master["ID"]
        .astype(str)
        .str.strip()
    )

    # Create lookups using ParameterMaster.ID

    parameter_name_lookup = (
        parameter_master
        .set_index("ID")["Name"]
        .to_dict()
    )

    # ---------------------------------------------------------
    # Build XML → Excel mapping
    # ---------------------------------------------------------
    mappings = []

    for item in root.iter("Item"):

        # -----------------------------
        # Parameter ID
        # -----------------------------
        parameter_id_element = item.find("ParameterID")

        if parameter_id_element is None:
            continue

        if not parameter_id_element.text:
            continue

        parameter_id = parameter_id_element.text.strip()

        if not parameter_id:
            continue

        # Only include parameters existing in ParameterMaster
        if parameter_id not in parameter_name_lookup:
            continue

        # -----------------------------
        # Data Type
        # -----------------------------
        data_type = item.findtext(
            "ValueDataType", ""
            ).strip()

        # -----------------------------
        # Access
        # -----------------------------
        access = item.get(
            "ReadWriteAccess",
            ""
        )

        # -----------------------------
        # PLC Parameter
        # -----------------------------
        plc_parameter = item.get(
            "ItemID",
            ""
        )

        # -----------------------------
        # PC Parameter
        # -----------------------------
        #
        # First check XML ParameterName.
        # If it is None, empty, or missing,
        # fall back to ParameterMaster.Name.
        # -----------------------------

        parameter_name_element = item.find("ParameterName")

        pc_parameter = parameter_name_lookup.get(
            parameter_id,
            ""
        )


        # -----------------------------
        # Add row
        # -----------------------------
        mappings.append({
            "Data Type": data_type,
            "Access": access,
            "PLC Parameter": plc_parameter,
            "PC Parameter": pc_parameter
        })

    # ---------------------------------------------------------
    # Create DataFrame
    # ---------------------------------------------------------
    mapping_df = pd.DataFrame(
        mappings,
        columns=[
            "Data Type",
            "Access",
            "PLC Parameter",
            "PC Parameter"
        ]
    )

    return mapping_df