from pathlib import Path
from argparse import ArgumentParser
import csv
import random


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPOSITORY_ROOT.parent / "WorkloadVista-Data"


REPORT_FILENAME = "machine_record_counts.csv"
OUTPUT_FILENAME = "selected_machines.txt"

DEFAULT_SEED = 42
DEFAULT_SAMPLE_SIZE = 5


def parse_arguments():
    parser = ArgumentParser(
        description="Select a reproducible random sample of machines."
    )

    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Path to the WorkloadVista data workspace.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        help="Number of distinct machines to select.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Random seed for reproducible selection.",
    )

    return parser.parse_args()


def select_machines(data_dir: Path, sample_size: int, seed: int):

    report_path = data_dir / "reports" / REPORT_FILENAME
    output_path = data_dir / "reports" / OUTPUT_FILENAME

    if not report_path.is_file():
        raise FileNotFoundError(f"Report not found at: {report_path}")

    if sample_size < 1:
        raise ValueError("Sample size must be at least 1.")

    machines = []

    with report_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            machines.append(
                {
                    "machine_id": row["machine_id"],
                    "record_count": int(row["record_count"]),
                }
            )

    if len(machines) < DEFAULT_SAMPLE_SIZE:
        raise ValueError("Not enough distinct machines to select five.")

    rng = random.Random(DEFAULT_SEED)
    selected = rng.sample(machines, DEFAULT_SAMPLE_SIZE)

    print("\n---- SELECTED MACHINES ----")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)

        writer.writerow(["machine_id", "record_count"])
        for i, machine in enumerate(selected, start=1):
            machine_id = machine["machine_id"]
            records_count = machine["record_count"]
            print(f"i. Machine ID: {machine_id} | Records: {records_count}")
            writer.writerow([machine_id, records_count])


if __name__ == "__main__":
    args = parse_arguments()
    select_machines(data_dir=args.data_dir, sample_size=args.sample_size, seed=args.seed )
