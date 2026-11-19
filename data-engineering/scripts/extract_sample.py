
from argparse import ArgumentParser
from pathlib import Path
import csv


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPOSITORY_ROOT.parent / "WorkloadVista-Data"

DATASET_FILENAME = "clusterdata_2019_b_instance_usage.csv"
SELECTION_FILENAME = "selected_machines.csv"
OUTPUT_FILENAME = "selected_machines_instance_usage.csv"


def parse_arguments():
    parser = ArgumentParser(
        description="Extract instance usage records for selected machines."
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Path to the WorkloadVista data workspace.",
    )

    return parser.parse_args()


def load_selected_machines(selection_path: Path):
    if not selection_path.is_file():
        raise FileNotFoundError(
            f"Machine selection file not found: {selection_path}"
        )

    selected_machines = {}

    with selection_path.open(
        "r", encoding="utf-8", newline=""
    ) as file:
        reader = csv.DictReader(file)

        required_columns = {"machine_id", "record_count"}

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                "Selection file must contain "
                "'machine_id' and 'record_count' columns."
            )

        for row_number, row in enumerate(reader, start=2):
            machine_id = (row["machine_id"] or "").strip()

            if not machine_id:
                raise ValueError(
                    f"Missing machine ID at selection row {row_number}."
                )

            if machine_id in selected_machines:
                raise ValueError(
                    f"Duplicate machine ID in selection: {machine_id}"
                )

            try:
                record_count = int(row["record_count"])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Invalid record count at selection row {row_number}."
                ) from None

            if record_count < 1:
                raise ValueError(
                    f"Record count must be positive at row {row_number}."
                )

            selected_machines[machine_id] = record_count

    if not selected_machines:
        raise ValueError("The machine selection file is empty.")

    return selected_machines


def extract_sample(data_dir: Path):
    dataset_path = data_dir / "raw" / DATASET_FILENAME
    selection_path = data_dir / "reports" / SELECTION_FILENAME
    output_path = data_dir / "samples" / OUTPUT_FILENAME

    if not dataset_path.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}"
        )

    selected_machines = load_selected_machines(selection_path)

    extracted_counts = {
        machine_id: 0 for machine_id in selected_machines
    }

    total_extracted = 0
    total_processed = 0

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("Starting sample extraction...")

    with dataset_path.open(
        "r", encoding="utf-8", newline=""
    ) as source:

        reader = csv.DictReader(source)

        if "machine_id" not in (reader.fieldnames or []):
            raise ValueError(
                "Required column 'machine_id' not found in dataset."
            )

        with output_path.open(
            "w", encoding="utf-8", newline=""
        ) as destination:

            writer = csv.DictWriter(
                destination,
                fieldnames=reader.fieldnames,
            )

            writer.writeheader()

            for row in reader:
                total_processed += 1

                if None in row or any(
                    value is None for value in row.values()
                ):
                    raise ValueError(
                        f"Malformed CSV record near line {reader.line_num}."
                    )

                machine_id = (row.get("machine_id") or "").strip()

                if machine_id in selected_machines:
                    writer.writerow(row)
                    extracted_counts[machine_id] += 1
                    total_extracted += 1

                if total_processed % 1_000_000 == 0:
                    print(
                        f"Processed {total_processed:,} records..."
                    )

    print("\n=== EXTRACTION RESULTS ===")
    print(f"Total processed records: {total_processed:,}")
    print(f"Total extracted records: {total_extracted:,}")

    mismatches = []

    for machine_id, expected_count in selected_machines.items():
        actual_count = extracted_counts[machine_id]
        status = "OK" if actual_count == expected_count else "MISMATCH"

        print(
            f"{machine_id}: expected {expected_count:,}, "
            f"extracted {actual_count:,} [{status}]"
        )

        if actual_count != expected_count:
            mismatches.append(machine_id)

    if mismatches:
        raise RuntimeError(
            "Extraction validation failed for machine IDs: "
            + ", ".join(mismatches)
        )

    print(f"\nSample saved to: {output_path}")
    print("Extraction and record-count validation successful.")


if __name__ == "__main__":
    args = parse_arguments()
    extract_sample(args.data_dir)
