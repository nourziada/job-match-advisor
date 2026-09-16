import os
import sys

from config import CV_DIR
from rag.indexer import build_index_from_path, file_fingerprint, needs_rebuild


def main():
    cv_path = os.path.join(CV_DIR, "my_cv.pdf")

    if not os.path.exists(cv_path):
        print(f"No CV found at {cv_path}")
        return

    with open(cv_path, "rb") as f:
        fingerprint = file_fingerprint(f.read())

    force = "--force" in sys.argv
    if not force and not needs_rebuild(fingerprint):
        print("Index is already up to date for this CV. Use --force to rebuild.")
        return

    print("Building the index...")
    count = build_index_from_path(cv_path)
    print(f"Index built successfully - {count} chunks.")


if __name__ == "__main__":
    main()
