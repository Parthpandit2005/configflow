def compare_vehicle_models(
    df_results,
    webpro_models
):

    webpro_names = set(
        webpro_models[
            "VehicleModelName"
        ]
        .dropna()
        .str.strip()
    )

    history_names = set(
        df_results[
            "vehicle_model"
        ]
        .dropna()
        .str.strip()
    )

    history_names.discard("")

    exact_matches = (
        webpro_names &
        history_names
    )

    unused_webpro = (
        webpro_names -
        history_names
    )

    unmatched_history = (
        history_names -
        webpro_names
    )

    return {
        "webpro_names": webpro_names,
        "history_names": history_names,
        "exact_matches": exact_matches,
        "unused_webpro": unused_webpro,
        "unmatched_history": unmatched_history
    }
def check_unmatched_models(
    df_results,
    unmatched_models
):

    mat_check = (
        df_results[
            df_results["vehicle_model"]
            .isin(unmatched_models)
        ]
        [
            [
                "vehicle_model",
                "vin"
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "vehicle_model",
                "vin"
            ]
        )
    )

    return mat_check