# CSV売上集計CLI

[![CI](https://github.com/thebitmoss/config-and-CI/actions/workflows/ci.yml/badge.svg)](https://github.com/thebitmoss/config-and-CI/actions/workflows/ci.yml)

CSVの売上データを読み込み、商品別の合計売上を表示する小さなPython CLIです。

## Features

- CSVファイルを商品別に集計
- text / json 出力に対応
- 商品名順 / 売上降順の並び替えに対応
- 商品列名、売上列名、文字コードをCLI引数で指定可能
- 不正な売上金額や不足列をエラーとして検知
- pytestとruffによるテスト・lint
- GitHub Actionsでpush / pull request時にCIを実行

## Requirements

- Python 3.9+
- make

## Setup

仮想環境を作成して有効化します。

```bash
python3 -m venv .venv
source .venv/bin/activate
```

開発用依存関係をインストールします。

```bash
python3 -m pip install ".[dev]"
```

`".[dev]"` は、このプロジェクト本体と開発用ツールの `pytest` / `ruff` をまとめてインストールする指定です。

## Usage

サンプルCSVを集計します。

```bash
make run
```

直接実行する場合は次のようにします。

```bash
python3 sales_summary.py data/sample_sales.csv
```

text出力の例です。

```text
商品別 合計売上
----------------
みかん: 1,500円
りんご: 2,100円
バナナ: 800円
```

JSONで出力する場合は `--format json` を使います。

```bash
python3 sales_summary.py data/sample_sales.csv --format json
```

```json
{"みかん": 1500, "りんご": 2100, "バナナ": 800}
```

並び順を指定する場合は `--sort` を使います。既定値は商品名順の `product` です。

```bash
python3 sales_summary.py data/sample_sales.csv --sort product
```

売上の高い順に並べる場合は `sales` を指定します。

```bash
python3 sales_summary.py data/sample_sales.csv --sort sales
```

列名や文字コードを指定する場合は、次のオプションを使います。

```bash
python3 sales_summary.py data/sample_sales.csv \
  --product-column product \
  --sales-column sales \
  --encoding utf-8 \
  --sort sales
```

## Development

テストを実行します。

```bash
make test
```

lintを実行します。

```bash
make lint
```

CI相当のチェックをまとめて実行します。

```bash
make ci
```

`make` を使わずに直接実行する場合は、次のコマンドでも同じです。

```bash
python3 -m pytest
python3 -m ruff check .
```

## Project Structure

```text
.
├── .github
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows
│       └── ci.yml
├── Makefile
├── README.md
├── pyproject.toml
├── setup.cfg
├── sales_summary.py
├── data
│   ├── sample_sales.csv
│   └── sample_sales_error.csv
└── tests
    └── test_sales_summary.py
```

各ファイルの役割です。

- `sales_summary.py`: CLI本体です。CSV読み込み、検証、集計、出力を行います。
- `tests/test_sales_summary.py`: pytestのテストです。正常系、異常系、JSON出力を確認します。
- `data/sample_sales.csv`: 動作確認用の正常なサンプルCSVです。
- `data/sample_sales_error.csv`: エラー確認用のサンプルCSVです。
- `Makefile`: よく使う開発コマンドを `make test` などの短い名前で実行できるようにします。
- `pyproject.toml`: pytestとruffの設定、ビルド設定を管理します。
- `setup.cfg`: プロジェクト情報と開発用依存関係を管理します。
- `.github/workflows/ci.yml`: GitHub Actionsでテストとlintを自動実行します。
- `.github/PULL_REQUEST_TEMPLATE.md`: Pull Request作成時の確認項目です。
