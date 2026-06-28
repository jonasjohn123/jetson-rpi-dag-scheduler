import argparse
import shutil
from pathlib import Path

# Temporary test image
SOURCE_IMAGE = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "safety"
    / "worker.jpg"
)


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--output",
        required=True
    )

    args = parser.parse_args()

    if not SOURCE_IMAGE.exists():
        raise FileNotFoundError(
            f"Source image not found: {SOURCE_IMAGE}"
        )

    output = Path(args.output)

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    shutil.copy(
        SOURCE_IMAGE,
        output
    )

    print("Frame captured.")


if __name__ == "__main__":
    main()