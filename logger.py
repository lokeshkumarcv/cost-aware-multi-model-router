import csv
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

LOG_DIR = BASE_DIR / "data"

LOG_FILE = LOG_DIR / "requests.csv"


HEADERS = [
    "timestamp",
    "request",
    "model",
    "confidence",
    "complexity",
    "escalated",
    "reason",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "actual_cost",
    "baseline_cost",
    "savings",
    "savings_percentage"
]


def initialize_log():

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not LOG_FILE.exists():

        with open(
            LOG_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=HEADERS
            )

            writer.writeheader()


def log_request(
    result,
    request
):

    initialize_log()

    confidence = result.get(
        "confidence"
    )

    if confidence is None:
        confidence = ""


    row = {
        "timestamp":
            datetime.now().isoformat(
                timespec="seconds"
            ),

        "request":
            request,

        "model":
            result.get(
                "model",
                ""
            ),

        "confidence":
            confidence,

        "complexity":
            result.get(
                "complexity",
                0
            ),

        "escalated":
            result.get(
                "escalated",
                False
            ),

        "reason":
            result.get(
                "escalation_reason",
                ""
            ) or "",

        "input_tokens":
            result.get(
                "input_tokens",
                0
            ),

        "output_tokens":
            result.get(
                "output_tokens",
                0
            ),

        "total_tokens":
            result.get(
                "total_tokens",
                0
            ),

        "actual_cost":
            result.get(
                "actual_cost",
                0
            ),

        "baseline_cost":
            result.get(
                "baseline_cost",
                0
            ),

        "savings":
            result.get(
                "savings",
                0
            ),

        "savings_percentage":
            result.get(
                "savings_percentage",
                0
            )
    }


    with open(
        LOG_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=HEADERS
        )

        writer.writerow(row)


def load_logs():

    initialize_log()

    rows = []

    with open(
        LOG_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            clean_row = {}

            for header in HEADERS:

                clean_row[header] = row.get(
                    header,
                    ""
                )

            rows.append(
                clean_row
            )

    return rows