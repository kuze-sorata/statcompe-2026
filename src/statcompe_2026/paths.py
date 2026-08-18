"""プロジェクト内パスの定義。"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
FIGURES_DIR = PROJECT_ROOT / "figures"
TABLES_DIR = PROJECT_ROOT / "tables"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"
REFERENCES_DIR = PROJECT_ROOT / "references"
REPORTS_DIR = PROJECT_ROOT / "reports"


def ensure_output_directories() -> None:
    """生成物の出力先を作成する。"""
    for path in (PROCESSED_DATA_DIR, FIGURES_DIR, TABLES_DIR):
        path.mkdir(parents=True, exist_ok=True)
