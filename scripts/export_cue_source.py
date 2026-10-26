"""Export only the caller-supplied authenticated place195 native inventory; no fits."""

import argparse
import json

from neuro.cue_source_export import export


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "inventory", "outer", "inner", "output", "revision"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    print(json.dumps(export(**vars(args)), sort_keys=True))


if __name__ == "__main__":
    main()
