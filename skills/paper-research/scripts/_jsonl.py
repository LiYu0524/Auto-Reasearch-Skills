import json
from typing import Dict, Iterable, Iterator, TextIO


def read_jsonl(path: str) -> Iterator[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def write_jsonl(items: Iterable[Dict], fp: TextIO) -> None:
    for item in items:
        fp.write(json.dumps(item, ensure_ascii=False) + "\n")

