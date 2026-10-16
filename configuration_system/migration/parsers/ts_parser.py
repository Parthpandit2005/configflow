import xml.etree.ElementTree as ET


def parse_ts_file(file_path):

    tree = ET.parse(file_path)
    root = tree.getroot()

    data = {
        "execution_id": None,
        "date": None,
        "vin": None,
        "vehicle_model": None,
        "project": None,
        "result": None,
        "conducted_tests": []
    }

    for parameter in root.iter("ResultParameter"):

        name = parameter.get("Name")
        value = parameter.get("Value")
        group = parameter.get("Group")

        # Basic test information
        if name == "TestReferenceName":
            data["execution_id"] = value

        elif name == "Date":
            data["date"] = value

        elif name == "VehicleNumber":
            data["vin"] = value

        elif name == "VehicleModelName":
            data["vehicle_model"] = value

        elif name == "ProjectName":
            data["project"] = value

        elif name == "TestResult":
            data["result"] = value

        # Find tests that were actually conducted
        elif name == "IsTestConducted":

            if str(value).strip().lower() == "true":
                data["conducted_tests"].append(group)

    return data