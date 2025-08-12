import argparse
import json

from tools import create_cfg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", required=True)
    parser.add_argument("--tmdb_id", required=True)
    parser.add_argument("--cfg", type=str, default=None)
    args = parser.parse_args()

    cfg = args.cfg
    if isinstance(cfg, str):
        create_cfg(args.season, args.tmdb_id, json.loads(cfg))
    else:
        create_cfg(args.season, args.tmdb_id)


if __name__ == "__main__":
    main()
