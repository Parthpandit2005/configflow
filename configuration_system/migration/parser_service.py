import pandas as pd

from migration.parsers.ts_parser import parse_ts_file


def parse_result_files(ts_files):

    all_results = []
    failed_files = []

    for file in ts_files:

        try:

            result = parse_ts_file(file)

            # Keep original file path
            # for traceability
            result["source_file"] = str(file)

            all_results.append(result)

        except Exception as e:

            failed_files.append({
                "file": str(file),
                "error": str(e)
            })

    df_results = pd.DataFrame(
        all_results
    )

    return df_results, failed_files