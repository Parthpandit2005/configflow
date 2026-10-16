import openpyxl
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

EXCEL_PATH = BASE_DIR / "source_data" / "project_001.xlsx"


workbook = openpyxl.load_workbook(
    EXCEL_PATH,
    data_only=True
)

worksheet = workbook.active

print("=" * 70)
print("EXCEL HEADERS")
print("=" * 70)

for column_number, cell in enumerate(worksheet[1], start=1):

    print(
        f"Column {column_number}: "
        f"value={repr(cell.value)}"
    )