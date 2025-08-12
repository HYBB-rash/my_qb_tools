import argparse

from tools import enqueue


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--category", default="")
    parser.add_argument("--tags", required=True, type=str)
    parser.add_argument("--content-path", required=True)
    args = parser.parse_args()

    tags_args: list[str] = str(args.tags).split(",")

    def _parse_kv(tag: str) -> tuple[str, str | int | dict[str, str | int]]:
        [k, v] = tag.split("=", 1)
        if k == "tmdb":
            id, value = v.split("-", 1)
            return (k, {"id": int(id), "name": value})
        if k == "season":
            return (k, int(v))
        return (k, v)

    enqueue(
        name=args.name,
        category=args.category,
        tags=dict([_parse_kv(tag) for tag in tags_args]),
        content_path=args.content_path,
    )


if __name__ == "__main__":
    main()
