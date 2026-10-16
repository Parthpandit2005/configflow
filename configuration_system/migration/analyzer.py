import pandas as pd


def prepare_results(df_results):

    df_results = df_results.copy()

    df_results["date"] = pd.to_datetime(
        df_results["date"],
        format="%d-%m-%Y %H:%M:%S",
        errors="coerce"
    )

    return df_results


def get_basic_statistics(df_results):

    return {
        "rows": len(df_results),

        "unique_vehicle_models":
            df_results["vehicle_model"].nunique(),

        "unique_projects":
            df_results["project"].nunique(),

        "unique_vins":
            df_results["vin"].nunique(),

        "result_counts":
            df_results["result"].value_counts(
                dropna=False
            ),

        "invalid_dates":
            df_results["date"].isna().sum()
    }

def analyze_vehicle_models(df_results):

    model_analysis = (
        df_results
        .groupby("vehicle_model")
        .agg(
            assigned_project=(
                "project",
                lambda x: ", ".join(
                    sorted(
                        x.dropna().unique()
                    )
                )
            ),

            VM_executions=(
                "execution_id",
                "count"
            ),

            unique_vins=(
                "vin",
                "nunique"
            ),

            VM_first_used=(
                "date",
                "min"
            ),

            VM_last_used=(
                "date",
                "max"
            ),

            VM_pass_count=(
                "result",
                lambda x: (
                    x == "PASS"
                ).sum()
            ),

            VM_fail_count=(
                "result",
                lambda x: (
                    x == "FAIL"
                ).sum()
            )
        )
        .reset_index()
    )

    model_analysis = model_analysis.sort_values(
        "VM_executions",
        ascending=False
    )

    return model_analysis

def analyze_vins(df_results):

    vin_summary = (
        df_results
        .groupby(
            [
                "vehicle_model",
                "vin"
            ]
        )
        .agg(
            vin_executions=(
                "execution_id",
                "count"
            ),

            vin_first_used=(
                "date",
                "min"
            ),

            vin_last_used=(
                "date",
                "max"
            ),

            vin_pass_count=(
                "result",
                lambda x: (
                    x == "PASS"
                ).sum()
            ),

            vin_fail_count=(
                "result",
                lambda x: (
                    x == "FAIL"
                ).sum()
            )
        )
        .reset_index()
    )

    return vin_summary

def create_migration_summary(
    vin_summary,
    model_analysis
):

    migration_summary = vin_summary.merge(
        model_analysis,
        on="vehicle_model",
        how="left"
    )

    migration_summary = (
        migration_summary.rename(
            columns={
                "vehicle_model":
                "Vehicle_Model (VM)"
            }
        )
    )

    return migration_summary

def analyze_conducted_tests(df_results):

    df_tests = df_results[
        [
            "execution_id",
            "vehicle_model",
            "project",
            "date",
            "conducted_tests"
        ]
    ].explode(
        "conducted_tests"
    )

    df_tests = df_tests.dropna(
        subset=["conducted_tests"]
    )

    return df_tests

def analyze_conducted_tests(df_results):

    df_tests = df_results[
        [
            "execution_id",
            "vehicle_model",
            "project",
            "date",
            "conducted_tests"
        ]
    ].explode(
        "conducted_tests"
    )

    df_tests = df_tests.dropna(
        subset=["conducted_tests"]
    )

    return df_tests

def find_blank_models(df_results):

    blank_models = df_results[
        df_results["vehicle_model"]
        .fillna("")
        .str.strip() == ""
    ]

    return blank_models

def filter_last_one_year(df_results):
    df_results = df_results.copy()

    if df_results.empty:
        return df_results

    latest_date = df_results["date"].max()

    one_year_ago = latest_date - pd.DateOffset(years=1)

    filtered_results = df_results[
        (df_results["date"] >= one_year_ago)
        & (df_results["date"] <= latest_date)
    ].copy()

    return filtered_results

def get_model_execution_details(df_results, vehicle_model):
    model_data = df_results[
        df_results["vehicle_model"] == vehicle_model
    ].copy()

    columns = [
        "execution_id",
        "vehicle_model",
        "project",
        "date",
        "conducted_tests",
        "failed_test_modes"
    ]

    available_columns = [
        column
        for column in columns
        if column in model_data.columns
    ]

    model_data = model_data[available_columns]

    # Make list-type fields easier to read in Streamlit
    for column in ["conducted_tests", "failed_test_modes"]:

        if column in model_data.columns:

            model_data[column] = model_data[column].apply(
                lambda value: (
                    ", ".join(map(str, value))
                    if isinstance(value, (list, tuple, set))
                    else (
                        "" if value is None else str(value)
                    )
                )
            )

    return model_data.sort_values(
        "date",
        ascending=True
    )