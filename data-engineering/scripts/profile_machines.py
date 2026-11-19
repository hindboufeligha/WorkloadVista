from pathlib import Path
from collections import Counter
from argparse import ArgumentParser
import csv
import statistics


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPOSITORY_ROOT.parent / "WorkloadVista-Data"

DATASET_FILENAME = "clusterdata_2019_b_instance_usage.csv"
REPORT_FILENAME = "machine_record_counts.csv"


def parse_arguments():
    parser = ArgumentParser(
        description="Profile machine-level record counts in a Borg trace CSV."
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Path to the WorkloadVista Data workspace.",
    )

    return parser.parse_args()


def profile_machines(data_dir: Path):

    dataset_path = data_dir / "raw" / DATASET_FILENAME
    report_path = data_dir / "reports" / REPORT_FILENAME

    if not dataset_path.is_file():
        raise FileNotFoundError(f"Dataset not found at: {dataset_path}")

    machine_counts = Counter()
    missing_machine_ids = 0
    malformed_rows = 0
    total_records = 0

    print("Starting dataset profiling..")

    with dataset_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if "machine_id" not in (reader.fieldnames or []):
            raise ValueError("machine_id column nit found")

        for row in reader:
            total_records += 1

            # detect rows with missing or unexpected CSV files
            if None in row or any(value is None for value in row.values()):
                malformed_rows += 1

            machine_id = (row.get("machine_id") or "").strip()

            if not machine_id:
                missing_machine_ids += 1
            else:
                machine_counts[machine_id] += 1

            if total_records % 1_000_000 == 0:
                print(f"Processed {total_records:,} records..")

    report_path.parent.mkdir(parents=True, exist_ok=True)

    with report_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["machine_id", "record_count"])

        for machine_id, count in sorted(machine_counts.items()):
            writer.writerow([machine_id, count])

    counts = list(machine_counts.values())

    print("\n---- PROFILING RESULTS ----")
    print(f"Total records: {total_records:,}")
    print(f"Distinct machines: {len(machine_counts):,}")
    print(f"Missing machine IDs: {missing_machine_ids:,}")
    print(f"Malformed rows: {malformed_rows:,}")

    if counts:
        print(f"Minimum records per machine: {min(counts):,}")
        print(f"Median records per machine: {statistics.median(counts):,.1f}")
        print(f"Maximum records per machine: {max(counts):,}")

    print(f"\nMachine report saved to: {REPORT_FILENAME}")


if __name__ == "__main__":
    args = parse_arguments()
    profile_machines(args.data_dir)
