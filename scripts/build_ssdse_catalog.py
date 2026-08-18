"""取得済みSSDSE A〜FからUTF-8の項目カタログを作成する。"""

from __future__ import annotations

import pandas as pd

from statcompe_2026.paths import PROJECT_ROOT, RAW_DATA_DIR, REFERENCES_DIR
from statcompe_2026.ssdse import catalog


def main() -> None:
    sources = sorted((RAW_DATA_DIR / "ssdse").glob("SSDSE-*.csv"))
    if not sources:
        raise FileNotFoundError("data/raw/ssdse にSSDSE CSVがありません")
    result = pd.concat([catalog(path) for path in sources], ignore_index=True)
    destination = REFERENCES_DIR / "ssdse_catalog.csv"
    result.to_csv(destination, index=False, encoding="utf-8-sig")
    summary = result.groupby(["dataset", "version"], sort=True).agg(
        columns=("column_index", "size"), data_rows=("data_rows", "first")
    )
    print(destination.relative_to(PROJECT_ROOT))
    print(summary.to_string())


if __name__ == "__main__":
    main()
