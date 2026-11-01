#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path
import argparse


def create_tmp_file(extension: str, directory: Path | None = None) -> Path:
    now = datetime.now()

    date_dir = now.strftime("%Y%m%d")
    filename = now.strftime("%H%M") + f".{extension.lstrip('.')}"

    directory = directory or Path.cwd() / "tmp"
    directory = directory / date_dir
    directory.mkdir(parents=True, exist_ok=True)

    file_path = directory / filename
    file_path.touch(exist_ok=True)

    return file_path


def main():
    parser = argparse.ArgumentParser(
        description="Create a temporary file in ./tmp/YYYYMMDD/"
    )
    parser.add_argument(
        "extension",
        help="File extension, e.g. html, svg, py, json",
    )
    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        help="Base directory for the temporary file",
    )

    args = parser.parse_args()

    path = create_tmp_file(args.extension, args.directory)
    print(path)


if __name__ == "__main__":
    main()
