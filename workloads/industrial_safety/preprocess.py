import argparse
from pathlib import Path

import cv2


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        required=True
    )

    parser.add_argument(
        "--output",
        required=True
    )

    args = parser.parse_args()

    image = cv2.imread(args.input)

    if image is None:
        raise FileNotFoundError(
            f"Unable to read image: {args.input}"
        )

    #
    # Resize
    #

    image = cv2.resize(
        image,
        (640, 640)
    )

    #
    # Future preprocessing goes here
    #
    # - denoising
    # - normalization
    # - histogram equalization
    #

    Path(args.output).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cv2.imwrite(
        args.output,
        image
    )

    print(
        "Preprocessing complete"
    )


if __name__ == "__main__":

    main()