import argparse
import json
from pathlib import Path


def point_inside_box(point_x, point_y, box):

    x1, y1, x2, y2 = box

    return (
        x1 <= point_x <= x2
        and
        y1 <= point_y <= y2
    )


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--persons",
        required=True
    )

    parser.add_argument(
        "--helmets",
        required=True
    )

    parser.add_argument(
        "--output",
        required=True
    )

    args = parser.parse_args()

    with open(args.persons) as f:

        persons = json.load(f)["detections"]

    with open(args.helmets) as f:

        helmets = json.load(f)["detections"]

    report = []

    for person_id, person in enumerate(persons, start=1):

        person_box = person["bbox"]

        status = "NO-Hardhat"

        confidence = None

        for helmet in helmets:

            hx1, hy1, hx2, hy2 = helmet["bbox"]

            center_x = (hx1 + hx2) / 2
            center_y = (hy1 + hy2) / 2

            if point_inside_box(
                center_x,
                center_y,
                person_box
            ):

                status = helmet["class"]
                confidence = helmet["confidence"]

                break

        report.append(

            {
                "person_id": person_id,
                "bbox": person_box,
                "status": status,
                "confidence": confidence
            }

        )

    Path(args.output).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(args.output, "w") as f:

        json.dump(

            {
                "persons": report
            },

            f,

            indent=4
        )

    safe = sum(
        p["status"] == "Hardhat"
        for p in report
    )

    unsafe = len(report) - safe

    print()

    print("========== REPORT ==========")

    print("Persons :", len(report))

    print("Safe    :", safe)

    print("Unsafe  :", unsafe)

    print()

    print("Report saved to")

    print(args.output)


if __name__ == "__main__":

    main()