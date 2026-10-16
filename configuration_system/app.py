from flask import Flask, render_template, request, send_file
from migration.service import (run_file_analysis, 
                               run_project_parameter_analysis,
                               run_project_parameter_mapping,
                               run_webpro_comparison)
from io import BytesIO
import pandas as pd

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/migration")
def migration():
    return render_template("migration.html")

@app.route("/migration/analysis", methods=["GET", "POST"])
def migration_analysis():

    analysis_result = None
    vehicle_models = []
    selected_model = None
    model_details = None

    if request.method == "POST":

        result_folder = request.form.get("result_folder", "").strip()
        selected_model = request.form.get("selected_model", "").strip()

        # WebPRO database details
        server = request.form.get("server", "").strip()
        database = request.form.get("database", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        auth_mode = request.form.get(
            "auth_mode",
            "Windows Authentication"
        )

        if result_folder:

            analysis_result = run_file_analysis(result_folder)

            vehicle_models = (
                analysis_result["model_analysis"]["vehicle_model"]
                .dropna()
                .astype(str)
                .tolist()
            )

            # Remove duplicates while preserving order
            vehicle_models = list(dict.fromkeys(vehicle_models))

            # Generate details for selected vehicle model
            if selected_model:

                df_results = analysis_result["df_results"]

                model_df = df_results[
                    df_results["vehicle_model"].astype(str) == selected_model
                ].copy()

                def count_test_cycles(value):

                    if value is None:
                        return 0

                    if isinstance(value, list):
                        return len(value)

                    value = str(value).strip()

                    if not value:
                        return 0

                    return len([
                        test.strip()
                        for test in value.split(",")
                        if test.strip()
                    ])

                model_df["test_cycles"] = model_df["conducted_tests"].apply(
                    count_test_cycles
                )

                execution_details = model_df[
                    [
                        "vin",
                        "execution_id",
                        "date",
                        "result",
                        "test_cycles",
                        "conducted_tests"
                    ]
                ].copy()

                vin_details = (
                    model_df
                    .groupby("vin")
                    .agg(
                        executions=("execution_id", "count"),
                        first_used=("date", "min"),
                        last_used=("date", "max"),
                        passed=("result", lambda x:
                            (x.astype(str).str.upper() == "PASS").sum()
                        ),
                        failed=("result", lambda x:
                            (x.astype(str).str.upper() == "FAIL").sum()
                        )
                    )
                    .reset_index()
                    .sort_values("executions", ascending=False)
                )

                model_details = {
                    "executions": len(model_df),
                    "vins": model_df["vin"].nunique(),
                    "pass": int(
                        (model_df["result"].astype(str).str.upper() == "PASS").sum()
                    ),
                    "fail": int(
                        (model_df["result"].astype(str).str.upper() == "FAIL").sum()
                    ),
                    "first_used": model_df["date"].min(),
                    "last_used": model_df["date"].max(),
                    "vin_details": vin_details,
                    "execution_details": execution_details
                }

            # WebPRO comparison
            print("===== WEBPRO DEBUG =====")
            print("SERVER:", server)
            print("DATABASE:", database)
            print("AUTH:", auth_mode)
            print("USERNAME:", username)
            print("========================")
            if server and database:

                analysis_result = run_webpro_comparison(
                    analysis_result,
                    server,
                    database,
                    username=username if username else None,
                    password=password if password else None,
                    auth_mode=auth_mode
                )

    return render_template(
        "migration_analysis.html",
        analysis_result=analysis_result,
        vehicle_models=vehicle_models,
        selected_model=selected_model,
        model_details=model_details,
    )

@app.route("/migration/parameter-analysis", methods=["GET", "POST"])
def migration_parameter_analysis():

    parameter_result = None

    if request.method == "POST":

        server = request.form.get("server", "").strip()
        database = request.form.get("database", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        auth_mode = request.form.get(
            "auth_mode",
            "Windows Authentication"
        )

        if server and database:

            parameter_result = run_project_parameter_analysis(
                server=server,
                database=database,
                username=username if username else None,
                password=password if password else None,
                auth_mode=auth_mode
            )

    return render_template(
        "parameter_analysis.html",
        parameter_result=parameter_result
    )
@app.route("/migration/parameter-analysis/download/used", methods=["POST"])
def download_used_parameters():

    server = request.form.get("server", "").strip()
    database = request.form.get("database", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    auth_mode = request.form.get(
        "auth_mode",
        "Windows Authentication"
    )

    parameter_result = run_project_parameter_analysis(
        server=server,
        database=database,
        username=username if username else None,
        password=password if password else None,
        auth_mode=auth_mode
    )

    df = parameter_result["used_parameters"]

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Used Parameters"
        )

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="used_parameters.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.route("/migration/parameter-analysis/download/unused", methods=["POST"])
def download_unused_parameters():

    server = request.form.get("server", "").strip()
    database = request.form.get("database", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    auth_mode = request.form.get(
        "auth_mode",
        "Windows Authentication"
    )

    parameter_result = run_project_parameter_analysis(
        server=server,
        database=database,
        username=username if username else None,
        password=password if password else None,
        auth_mode=auth_mode
    )

    df = parameter_result["unused_parameters"]

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Unused Parameters"
        )

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="unused_parameters.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/migration/parameter-mapping", methods=["GET", "POST"])
def migration_parameter_mapping():

    mapping_result = None

    if request.method == "POST":

        server = request.form.get("server", "").strip()
        database = request.form.get("database", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        auth_mode = request.form.get(
            "auth_mode",
            "Windows Authentication"
        )

        if server and database:

            mapping_result = run_project_parameter_mapping(
                server=server,
                database=database,
                username=username if username else None,
                password=password if password else None,
                auth_mode=auth_mode
            )

    return render_template(
        "parameter_mapping.html",
        mapping_result=mapping_result
    )

@app.route("/migration/parameter-mapping/download", methods=["POST"])
def download_parameter_mapping():

    server = request.form.get("server", "").strip()
    database = request.form.get("database", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    auth_mode = request.form.get(
        "auth_mode",
        "Windows Authentication"
    )

    mapping_result = run_project_parameter_mapping(
        server=server,
        database=database,
        username=username if username else None,
        password=password if password else None,
        auth_mode=auth_mode
    )

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        mapping_result.to_excel(
            writer,
            index=False,
            sheet_name="Parameter Mapping"
        )

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="parameter_mapping.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )