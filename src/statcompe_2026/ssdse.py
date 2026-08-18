"""SSDSE公式CSVのヘッダー構造を吸収する読み込み補助。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class SSDSELayout:
    dataset: str
    metadata_rows: int
    code_row: int
    label_row: int
    period_row: int | None


LAYOUTS = {
    "A": SSDSELayout("A", 3, 0, 2, 1),
    "B": SSDSELayout("B", 2, 0, 1, None),
    "C": SSDSELayout("C", 2, 0, 1, None),
    "D": SSDSELayout("D", 2, 0, 1, None),
    "E": SSDSELayout("E", 3, 0, 2, 1),
    "F": SSDSELayout("F", 2, 0, 1, None),
}


def dataset_letter(path: Path) -> str:
    match = re.match(r"SSDSE-([A-F])-", path.name, flags=re.IGNORECASE)
    if match is None:
        raise ValueError(f"SSDSEファイル名ではありません: {path.name}")
    return match.group(1).upper()


def read_raw(path: Path) -> pd.DataFrame:
    """公式配布CSVを文字列のまま読み込む。"""
    return pd.read_csv(path, encoding="cp932", header=None, dtype=str)


def catalog(path: Path) -> pd.DataFrame:
    """1ファイルの全列を、コード・名称・対象時点の一覧にする。"""
    letter = dataset_letter(path)
    layout = LAYOUTS[letter]
    raw = read_raw(path)
    codes = raw.iloc[layout.code_row].fillna("").astype(str)
    labels = raw.iloc[layout.label_row].fillna("").astype(str)
    if layout.period_row is None:
        periods = pd.Series([""] * raw.shape[1])
    else:
        periods = raw.iloc[layout.period_row].fillna("").astype(str)

    return pd.DataFrame(
        {
            "dataset": letter,
            "version": path.stem.removeprefix(f"SSDSE-{letter}-"),
            "column_index": range(raw.shape[1]),
            "code": codes,
            "label": labels,
            "period": periods,
            "data_rows": raw.shape[0] - layout.metadata_rows,
        }
    )
