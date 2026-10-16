from pathlib import Path


def export_migration_summary(
    migration_summary,
    output_path
):

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    migration_summary.to_csv(
        output_path,
        index=False
    )

    return output_path