from pathlib import Path

import pytest

from statcompe_2026.ssdse import dataset_letter


def test_dataset_letter() -> None:
    assert dataset_letter(Path("SSDSE-F-2023v3.csv")) == "F"


def test_dataset_letter_rejects_other_names() -> None:
    with pytest.raises(ValueError):
        dataset_letter(Path("other.csv"))
