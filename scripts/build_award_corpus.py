"""受賞論文PDFを抽出・索引化し、1論文1枚の読書カードを作る。"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

from statcompe_2026.paths import PROJECT_ROOT, REFERENCES_DIR

METHOD_PATTERNS = {
    "記述統計・可視化": r"記述統計|可視化|ヒストグラム|散布図|箱ひげ",
    "相関分析": r"相関(係数|分析)?|correlation",
    "重回帰": r"重回帰|multiple regression|OLS|最小二乗",
    "パネルデータ": r"パネルデータ|固定効果|変量効果|Hausman|ハウスマン",
    "時系列": r"時系列|ARIMA|VAR|グレンジャー|インパルス応答",
    "主成分分析": r"主成分分析|PCA",
    "因子分析": r"因子分析",
    "クラスタリング": r"クラスタ(ー|リング)|k-means|階層的",
    "空間分析": r"空間(回帰|自己相関|分析)|Moran|GIS|地理的加重",
    "検定": r"t検定|カイ二乗|Kruskal|Dunn|分散分析|有意水準",
    "機械学習": r"ランダムフォレスト|勾配ブースティング|XGBoost|機械学習|決定木",
    "因果推論": r"差の差|傾向スコア|操作変数|回帰不連続|因果推論",
}

THEME_PATTERNS = {
    "人口・移住": r"人口|移住|転入|転出|過疎|地方創生",
    "教育": r"教育|学力|学校|教員|大学|不登校",
    "健康・医療": r"健康|医療|医師|疾患|寿命|死亡|病院",
    "福祉・子育て": r"福祉|子育て|保育|待機児童|介護|社会保障",
    "労働・経済": r"労働|雇用|賃金|所得|景気|産業|経済",
    "環境・エネルギー": r"環境|ごみ|リサイクル|脱炭素|電力|気候|温暖化",
    "防災・安全": r"災害|震災|防災|火災|犯罪|交通事故",
    "政治・行政": r"投票|議員|選挙|行政|政策|財政",
    "観光・文化": r"観光|文化|スポーツ|余暇",
}


def tags(text: str, patterns: dict[str, str]) -> list[str]:
    return [name for name, pattern in patterns.items() if re.search(pattern, text, re.I)]


def extract_text(path: Path) -> tuple[int, str]:
    reader = PdfReader(path)
    pages = [(page.extract_text() or "") for page in reader.pages]
    return len(pages), "\n\n".join(pages)


def compact_excerpt(text: str, heading_pattern: str, limit: int = 650) -> str:
    normalized = re.sub(r"[ \t]+", " ", text)
    match = re.search(heading_pattern, normalized, re.I)
    if match is None:
        return ""
    excerpt = normalized[match.start() : match.start() + limit]
    return re.sub(r"\n{3,}", "\n\n", excerpt).strip()


def note_markdown(row: pd.Series) -> str:
    official = row["official_summary"] if pd.notna(row["official_summary"]) else ""
    summary = official or "公式ページに個別紹介文なし。本文抽出メモを起点に精読する。"
    methods = row["method_tags"] or "未検出"
    themes = row["theme_tags"] or "未分類"
    purpose = row["purpose_excerpt"] or "（見出しを自動検出できず）"
    conclusion = row["conclusion_excerpt"] or "（見出しを自動検出できず）"
    return f"""# {row["title"]}

## 書誌情報

- 年度: {row["year"]}
- 部門: {row["division"]}
- 賞: {row["award"]}
- 著者・所属: {row["author_affiliation"]}
- ページ数: {row["page_count"]}
- 公式PDF: {row["url"]}
- ローカル原本: `{row["local_path"]}`

## 概要

{summary}

## 自動索引

- テーマ: {themes}
- 手法: {methods}
- 本文抽出文字数: {row["character_count"]}

## 本文抽出メモ（機械抽出・精読時に要確認）

### 目的付近

{purpose}

### 結論付近

{conclusion}

## 精読レビュー

- [ ] 問いと社会的意義
- [ ] データ、単位、期間、前処理
- [ ] 手法選択と仮定
- [ ] 結果と主張の対応
- [ ] 限界・代替説明・頑健性
- [ ] 自分の論文へ転用できる設計上の学び
"""


def main() -> None:
    manifest = pd.read_csv(REFERENCES_DIR / "manifests" / "awards.csv")
    papers = manifest[manifest["kind"] == "paper"].copy()
    records: list[dict[str, object]] = []
    for _, source in papers.iterrows():
        pdf_path = PROJECT_ROOT / source["local_path"]
        division_slug = (
            "high-school" if source["division"] == "高校生の部" else "university-general"
        )
        paper_id = pdf_path.stem
        text_path = (
            REFERENCES_DIR
            / "awards"
            / "text"
            / str(source["year"])
            / division_slug
            / f"{paper_id}.txt"
        )
        note_path = (
            REFERENCES_DIR
            / "awards"
            / "notes"
            / str(source["year"])
            / division_slug
            / f"{paper_id}.md"
        )
        text_path.parent.mkdir(parents=True, exist_ok=True)
        note_path.parent.mkdir(parents=True, exist_ok=True)
        page_count = len(PdfReader(pdf_path).pages)
        if text_path.exists():
            text = text_path.read_text(encoding="utf-8")
        else:
            _, text = extract_text(pdf_path)
            text_path.write_text(text, encoding="utf-8")
        combined = f"{source['title']}\n{source.get('official_summary', '')}\n{text}"
        thematic_text = f"{source['title']}\n{source.get('official_summary', '')}"
        record = source.to_dict() | {
            "paper_id": paper_id,
            "page_count": page_count,
            "character_count": len(text),
            "method_tags": " / ".join(tags(combined, METHOD_PATTERNS)),
            "theme_tags": " / ".join(tags(thematic_text, THEME_PATTERNS)),
            "purpose_excerpt": compact_excerpt(
                text, r"(?:研究|分析)?(?:の)?目的|はじめに|問題意識"
            ),
            "conclusion_excerpt": compact_excerpt(text, r"結論|まとめ|おわりに|考察"),
            "text_path": text_path.relative_to(PROJECT_ROOT).as_posix(),
            "note_path": note_path.relative_to(PROJECT_ROOT).as_posix(),
        }
        note_path.write_text(note_markdown(pd.Series(record)), encoding="utf-8")
        records.append(record)

    index = pd.DataFrame(records)
    index_path = REFERENCES_DIR / "awards" / "index.csv"
    index.to_csv(index_path, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)

    summaries = manifest[manifest["kind"] == "judging_summary"]
    for _, source in summaries.iterrows():
        pdf_path = PROJECT_ROOT / source["local_path"]
        _, text = extract_text(pdf_path)
        text_path = REFERENCES_DIR / "awards" / "text" / str(source["year"]) / "judging-summary.txt"
        text_path.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if text_path.exists() else "w"
        with text_path.open(mode, encoding="utf-8") as stream:
            if mode == "a":
                stream.write("\n\n")
            stream.write(text)
    print(f"Indexed {len(index)} papers")
    print(index.groupby(["year", "division"]).size().to_string())
    print(index_path.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
