"""2018〜2025年の公式受賞論文・審査総評を取得し、台帳を作る。"""

from __future__ import annotations

import csv
import hashlib
import re
import unicodedata
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup, Tag

from statcompe_2026.paths import PROJECT_ROOT, REFERENCES_DIR

YEARS = range(2018, 2026)
PAGE_URL = "https://www.nstac.go.jp/statcompe/past/award-{year}/"


@dataclass(frozen=True)
class AwardRow:
    year: int
    kind: str
    division: str
    award: str
    title: str
    author_affiliation: str
    official_summary: str
    url: str
    local_path: str
    retrieved_at: str
    sha256: str
    bytes: int


def clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\(PDF[^)]*\)|（PDF[^）]*）", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip(" 　-–—")


def safe_name(name: str) -> str:
    name = re.sub(r"[<>:\"/\\|?*]", "_", name)
    return re.sub(r"\s+", "_", name).strip("._")[:120]


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def following_paragraphs(heading: Tag) -> tuple[str, str]:
    paragraphs: list[str] = []
    for sibling in heading.next_siblings:
        if isinstance(sibling, Tag) and sibling.name in {"h2", "h3", "h4"}:
            break
        if isinstance(sibling, Tag) and sibling.name == "p":
            value = clean(sibling.get_text(" ", strip=True))
            if value:
                paragraphs.append(value)
        if len(paragraphs) >= 2:
            break
    return (paragraphs + ["", ""])[:2]


def download(session: requests.Session, url: str) -> bytes:
    response = session.get(url, timeout=90)
    response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        raise ValueError(f"PDFではない応答です: {url}")
    return response.content


def parse_year(session: requests.Session, year: int) -> list[AwardRow]:
    page_url = PAGE_URL.format(year=year)
    response = session.get(page_url, timeout=60)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "lxml")
    retrieved_at = datetime.now(UTC).isoformat()
    rows: list[AwardRow] = []
    seen: set[str] = set()
    division = "共通"
    award = ""

    for element in soup.select("h2, h3, h4, p, li"):
        text = clean(element.get_text(" ", strip=True))
        if element.name == "h2" and "部" in text:
            division = "高校生の部" if "高校" in text else "大学生・一般の部"
        elif element.name == "h3":
            award = text

        for anchor in element.find_all("a", href=True):
            url = urljoin(page_url, anchor["href"])
            if not urlsplit(url).path.lower().endswith(".pdf") or url in seen:
                continue
            anchor_text = clean(anchor.get_text(" ", strip=True))
            is_paper = element.name == "h4" and division != "共通"
            is_commentary = "総評" in (text + anchor_text)
            if not (is_paper or is_commentary):
                continue
            seen.add(url)
            kind = "paper" if is_paper else "judging_summary"
            title = clean(text if is_paper else anchor_text or text)
            author, summary = following_paragraphs(element) if is_paper else ("", "")
            content = download(session, url)
            folder = REFERENCES_DIR / "awards" / "raw" / str(year) / (
                "high-school" if division == "高校生の部" else
                "university-general" if division == "大学生・一般の部" else "common"
            )
            source_name = Path(urlsplit(url).path).name
            filename = safe_name(source_name or f"{kind}.pdf")
            destination = folder / filename
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            rows.append(
                AwardRow(
                    year=year,
                    kind=kind,
                    division=division if is_paper else "共通",
                    award=award if is_paper else "",
                    title=title,
                    author_affiliation=author,
                    official_summary=summary,
                    url=url,
                    local_path=destination.relative_to(PROJECT_ROOT).as_posix(),
                    retrieved_at=retrieved_at,
                    sha256=sha256(content),
                    bytes=len(content),
                )
            )
    return rows


def main() -> None:
    session = requests.Session()
    session.headers["User-Agent"] = "statcompe-2026 research project"
    rows = [row for year in YEARS for row in parse_year(session, year)]
    if not rows:
        raise RuntimeError("受賞資料を検出できませんでした")
    destination = REFERENCES_DIR / "manifests" / "awards.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(asdict(rows[0])))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
    print(f"Downloaded {len(rows)} files")
    for year in YEARS:
        papers = sum(row.year == year and row.kind == "paper" for row in rows)
        comments = sum(row.year == year and row.kind == "judging_summary" for row in rows)
        print(f"{year}: papers={papers}, judging_summaries={comments}")
    print(destination.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
