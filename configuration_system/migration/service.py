from migration.scanner import find_ts_files
from migration.parser_service import parse_result_files

from migration.analyzer import (
    filter_last_one_year,
    prepare_results,
    get_basic_statistics,
    analyze_vehicle_models,
    analyze_vins,
    create_migration_summary,
    analyze_conducted_tests,
    find_blank_models
)

from migration.database import (
    connect_webpro,
    get_webpro_models,
    compare_project_parameters,
    build_project_parameter_mapping
)

from migration.comparison import (
    compare_vehicle_models
)

def run_file_analysis(result_folder):
    ts_files = find_ts_files(result_folder)

    df_results, failed_files = parse_result_files(ts_files)

    df_results = prepare_results(df_results)

    # --------------------------------------------------------
    # FULL HISTORY ANALYSIS
    # --------------------------------------------------------

    statistics = get_basic_statistics(df_results)

    model_analysis = analyze_vehicle_models(df_results)

    vin_summary = analyze_vins(df_results)

    migration_summary = create_migration_summary(
        vin_summary,
        model_analysis
    )

    df_tests = analyze_conducted_tests(df_results)

    blank_models = find_blank_models(df_results)

    # --------------------------------------------------------
    # LAST ONE YEAR DATA
    # --------------------------------------------------------

    df_last_one_year = filter_last_one_year(df_results)

    return {
        # Raw / full data
        "ts_files": ts_files,
        "df_results": df_results,
        "failed_files": failed_files,

        # Full history analysis
        "statistics": statistics,
        "model_analysis": model_analysis,
        "vin_summary": vin_summary,
        "migration_summary": migration_summary,
        "df_tests": df_tests,
        "blank_models": blank_models,

        # Last one year
        "df_last_one_year": df_last_one_year
    }

def run_webpro_comparison(
    analysis,
    server,
    database,
    username=None,
    password=None,
    auth_mode="Windows Authentication"
):
    connection = None

    try:
        connection = connect_webpro(
            server=server,
            database=database,
            username=username,
            password=password,
            auth_mode=auth_mode
        )

        webpro_models = (
            get_webpro_models(
                connection
            )
        )

        comparison = (
            compare_vehicle_models(
                analysis["df_results"],
                webpro_models
            )
        )

        analysis["webpro_models"] = (
            webpro_models
        )

        analysis["comparison"] = (
            comparison
        )

        return analysis

    finally:
        if connection is not None:
            connection.close()

def run_project_parameter_analysis(
    server,
    database,
    username=None,
    password=None,
    auth_mode="Windows Authentication"
):
    connection = None

    try:
        connection = connect_webpro(
            server,
            database,
            username,
            password,
            auth_mode
        )

        return compare_project_parameters(connection)

    finally:
        if connection is not None:
            connection.close()

def run_project_parameter_mapping(
    server,
    database,
    username=None,
    password=None,
    auth_mode="Windows Authentication"
):
    connection = None

    try:
        connection = connect_webpro(
            server,
            database,
            username,
            password,
            auth_mode
        )

        return build_project_parameter_mapping(connection)

    finally:
        if connection is not None:
            connection.close()