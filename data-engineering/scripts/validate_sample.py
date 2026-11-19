from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import csv


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPOSITORY_ROOT.parent / "WorkloadVista-Data"

SELECTION_FILENAME = "selected_machines.csv"
SAMPLE_FILENAME = "selected_machines_instance_usage.csv"

EXPECTED_COLUMNS = [
    "start_time",
    "end_time",
    "collection_id",
    "instance_index",
    "machine_id",
    "alloc_collection_id",
    "alloc_instance_index",
    "collection_type",
    "average_usage",
    "maximum_usage",
    "random_sample_usage",
    "cpu_usage_distribution",
    "tail_cpu_usage_distribution",
]


def parse_arguments():
    parser = ArgumentParser(description="Validate the extracted machine usage sample.")

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Path to the WorkloadVista data workspace.",
    )

    return parser.parse_args()


def load_selected_machines(selection_path: Path):
    if not selection_path.is_file():
        raise FileNotFoundError(f"Machine selection file not found: {selection_path}")

    selected_machines = {}

    with selection_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        required_columns = {"machine_id", "record_count"}

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                "Selection file must contain 'machine_id' and 'record_count' columns."
            )

        for row_number, row in enumerate(reader, start=2):
            machine_id = (row["machine_id"] or "").strip()

            if not machine_id:
                raise ValueError(f"Missing machine ID at selection row {row_number}.")

            if machine_id in selected_machines:
                raise ValueError(f"Duplicate machine ID in selection: {machine_id}")

            try:
                record_count = int(row["record_count"])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Invalid record count at selection row {row_number}."
                ) from None

            if record_count < 1:
                raise ValueError(f"Record count must be positive at row {row_number}.")

            selected_machines[machine_id] = record_count

    if not selected_machines:
        raise ValueError("The machine selection file is empty.")

    return selected_machines


def validate_sample(data_dir: Path):
    selection_path = data_dir / "reports" / SELECTION_FILENAME
    sample_path = data_dir / "samples" / SAMPLE_FILENAME

    if not sample_path.is_file():
        raise FileNotFoundError(f"Sample file not found: {sample_path}")

    selected_machines = load_selected_machines(selection_path)

    counts = Counter()
    total_records = 0
    malformed_records = 0
    errors = []

    with sample_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        columns = reader.fieldnames

        if columns is None:
            raise ValueError("Sample CSV is missing its header row.")

        if columns != EXPECTED_COLUMNS:
            errors.append("Sample columns do not match the expected 13-column schema.")

        if len(columns) != len(set(columns)):
            errors.append("Sample contains duplicate column names.")

        if "machine_id" not in columns:
            raise ValueError("Required column 'machine_id' not found in sample.")

        for row in reader:
            total_records += 1

            if None in row or any(value is None for value in row.values()):
                malformed_records += 1
                continue

            machine_id = (row.get("machine_id") or "").strip()

            if not machine_id:
                malformed_records += 1
                continue

            counts[machine_id] += 1

    unexpected_ids = set(counts) - set(selected_machines)
    missing_ids = set(selected_machines) - set(counts)

    for machine_id, expected_count in selected_machines.items():
        actual_count = counts[machine_id]

        if actual_count != expected_count:
            errors.append(
                f"Machine {machine_id}: expected {expected_count:,} "
                f"records, found {actual_count:,}."
            )

    if unexpected_ids:
        errors.append(f"Unexpected machine IDs: {sorted(unexpected_ids)}")

    if missing_ids:
        errors.append(f"Missing machine IDs: {sorted(missing_ids)}")

    if malformed_records:
        errors.append(f"Found {malformed_records:,} malformed records.")

    expected_total = sum(selected_machines.values())

    if total_records != expected_total:
        errors.append(
            f"Expected {expected_total:,} total records, found {total_records:,}."
        )

    print("\n=== SAMPLE VALIDATION ===")
    print(f"Total records: {total_records:,}")
    print(f"Number of columns: {len(columns)}")
    print(f"Distinct machines: {len(counts)}")
    print(f"Malformed records: {malformed_records:,}")

    print("\nMachine record counts:")

    for machine_id, expected_count in selected_machines.items():
        actual_count = counts[machine_id]
        status = "PASS" if actual_count == expected_count else "FAIL"

        print(f"{machine_id}: {actual_count:,} / {expected_count:,} - {status}")

    print(f"\nExpected columns: {columns}")

    if errors:
        print("\nVALIDATION FAILED")

        for error in errors:
            print(f"- {error}")

        raise ValueError("Sample validation failed.")

    print("\nAll validation checks passed.")
    print(f"Validated sample: {sample_path}")


if __name__ == "__main__":
    args = parse_arguments()
    validate_sample(args.data_dir)
