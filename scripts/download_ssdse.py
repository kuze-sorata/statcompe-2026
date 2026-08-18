"""SSDSE A〜Fの最新CSV・解説・項目一覧を公式ページから取得する。"""

from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from statcompe_2026.paths import PROJECT_ROOT, RAW_DATA_DIR, REFERENCES_DIR

INDEX_URL = "https://www.nstac.go.jp/use/literacy/ssdse/"
DATASET_RE = re.compile(r"SSDSE-([A-F])-[^/]+\.csv$", re.IGNORECASE)
GUIDE_RE = re.compile(r"kaisetsu-([A-F])-[^/]+\.pdf$", re.IGNORECASE)


@dataclass(frozen=True)
class ManifestRow:
    dataset: str
    kind: str
    filename: str
    url: str
    retrieved_at: str
    sha256: str
    bytes: int


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def download(session: requests.Session, url: str, destination: Path) -> ManifestRow:
    response = session.get(url, timeout=60)
    response.raise_for_status()
    content = response.content
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    filename = destination.name
    dataset_match = re.search(r"(?:SSDSE|kaisetsu)-([A-F])-", filename, re.IGNORECASE)
    dataset = dataset_match.group(1).upper() if dataset_match else "ALL"
    return ManifestRow(
        dataset=dataset,
        kind="data" if destination.suffix.lower() == ".csv" else "documentation",
        filename=filename,
        url=url,
        retrieved_at=datetime.now(UTC).isoformat(),
        sha256=sha256_bytes(content),
        bytes=len(content),
    )


def discover_urls(session: requests.Session) -> list[tuple[str, Path]]:
    response = session.get(INDEX_URL, timeout=60)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")

    data_urls: dict[str, str] = {}
    guide_urls: dict[str, str] = {}
    item_list_url: str | None = None

    for anchor in soup.find_all("a", href=True):
        url = urljoin(INDEX_URL, anchor["href"])
        filename = Path(url.split("?", 1)[0]).name
        text = anchor.get_text(" ", strip=True)
        if match := DATASET_RE.search(filename):
            data_urls.setdefault(match.group(1).upper(), url)
        elif match := GUIDE_RE.search(filename):
            guide_urls.setdefault(match.group(1).upper(), url)
        elif "SSDSE収録項目の一覧" in text and filename.lower().endswith(".xlsx"):
            item_list_url = url

    missing_data = sorted(set("ABCDEF") - set(data_urls))
    missing_guides = sorted(set("ABCDEF") - set(guide_urls))
    if missing_data or missing_guides or item_list_url is None:
        raise RuntimeError(
            f"公式ページのリンク検出に失敗: "
            f"missing_data={missing_data}, missing_guides={missing_guides}, "
            f"item_list={item_list_url}"
        )

    targets: list[tuple[str, Path]] = []
    for dataset in "ABCDEF":
        data_url = data_urls[dataset]
        guide_url = guide_urls[dataset]
        targets.append((data_url, RAW_DATA_DIR / "ssdse" / Path(data_url).name))
        targets.append(
            (guide_url, REFERENCES_DIR / "official" / "ssdse" / Path(guide_url).name)
        )
    targets.append(
        (
            item_list_url,
            REFERENCES_DIR / "official" / "ssdse" / Path(item_list_url).name,
        )
    )
    return targets


def write_manifest(rows: list[ManifestRow]) -> Path:
    manifest_path = REFERENCES_DIR / "manifests" / "ssdse.csv"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(asdict(rows[0])))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
    return manifest_path


def main() -> None:
    session = requests.Session()
    session.headers["User-Agent"] = "statcompe-2026 research project"
    rows = [download(session, url, destination) for url, destination in discover_urls(session)]
    manifest_path = write_manifest(rows)
    print(f"Downloaded {len(rows)} files")
    print(f"Manifest: {manifest_path.relative_to(PROJECT_ROOT)}")
    for row in rows:
        print(f"{row.dataset} {row.kind:13} {row.filename} {row.bytes:,} bytes")


if __name__ == "__main__":
    main()
