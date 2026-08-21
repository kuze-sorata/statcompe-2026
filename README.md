# statcompe-2026

統計データ分析コンペティション2026に向けた分析プロジェクト。

## Goal

- SSDSEを中心に、公的統計データを用いた課題設定、分析、示唆、提案を行う
- 論文として説明可能な分析プロセスを残す
- 受賞を目指しつつ、外部に見えるデータ分析実績として整理する

## Project Structure

```text
statcompe-2026/
├── project/
│   ├── STATUS.md
│   ├── selected-theme.md
│   ├── workflow.md
│   ├── requirements.md
│   └── registration.local.md
├── references/
│   ├── official/
│   │   ├── 2026/
│   │   └── ssdse/
│   ├── awards/
│   ├── manifests/
│   ├── library.csv
│   └── bibliography.bib
├── data/
│   ├── raw/
│   ├── external/
│   └── processed/
├── notebooks/
├── experiments/
├── session-logs/
├── reports/
├── figures/
├── tables/
└── src/
```

## AI Usage Policy

募集要項では、ChatGPT等の生成AIツールにより論文を作成することは認められていない。

このプロジェクトでは、生成AIを以下の補助用途に限定する。

- テーマ整理、分析計画、論点の壁打ち
- データ取得、前処理、可視化、分析コードの相談
- 統計手法や解釈の確認
- 自分で書いた文章に対する論理の抜け漏れ、言い過ぎ、誤字脱字のレビュー

以下は行わない。

- 論文本体や要旨を生成AIに新規作成させる
- 生成AIの文章をそのまま提出する
- 主張、結論、提案を生成AI主導で決める

最終的な論文、要旨、主張、提案は、自分の言葉で書き、自分で説明できる状態にする。

## Workflow

1. テーマ候補を広く出す
2. SSDSEと外部統計データの利用可能性を確認する
3. 受賞論文を読み、問いの立て方を学ぶ
4. テーマを絞り、仮説と分析方針を決める
5. Notebookで分析し、図表を `figures/` と `tables/` に残す
6. `experiments/` に試行錯誤を記録する
7. `reports/` で論文構成、要旨、参考文献を管理する

## Project Requirements

- コンペの応募条件、提出要件、進め方は `project/requirements.md` で管理する
- 登録メールアドレスなどの個人情報は、Git管理対象外の `project/registration.local.md` で管理する
- 公式の募集要項と提出テンプレートは `references/official/2026/` で原本を保管する

## Start Here

1. `project/STATUS.md` で現在地、未決定事項、次の完了条件を確認する
2. `project/requirements.md` で応募・提出要件を確認する
3. `project/workflow.md` で役割分担と日次の進め方を確認する
4. `references/ssdse_catalog.csv` で利用可能なSSDSE項目を探す
5. `references/awards/index.csv` と `references/awards/cross-year-synthesis.md` で過去受賞論文を参照する
6. 分析ごとに `experiments/registry.csv` と実験Markdownを更新する
7. 作業終了時に `project/STATUS.md` を更新し、作業履歴を `session-logs/` に残す

## Rebuild Commands

```powershell
uv sync
uv run python scripts/download_ssdse.py
uv run python scripts/build_ssdse_catalog.py
uv run python scripts/download_awards.py
uv run python scripts/build_award_corpus.py
uv run pytest -q
uv run ruff check .
```
