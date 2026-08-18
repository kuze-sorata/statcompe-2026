from statcompe_2026.paths import PROJECT_ROOT


def test_project_root_contains_readme() -> None:
    assert (PROJECT_ROOT / "README.md").is_file()
