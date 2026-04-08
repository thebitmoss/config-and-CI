# CSV売上集計CLI

## 1. 要件整理

目的は、CSVファイルの売上データを読み込み、商品別の合計売上を表示するCLIツールを作ることです。

今回の最小要件は次の通りです。

- コマンドラインからCSVファイルのパスを受け取る
- CSVにはヘッダー行がある
- 商品名の列は `product`
- 売上金額の列は `sales`
- 同じ商品が複数行に分かれていても、商品ごとに合計する
- 結果をターミナルに表示する
- CSVファイルが見つからない、列が足りない、数値でない売上がある場合はエラーを表示する

## 2. 最小実装の方針

Python標準ライブラリだけで実装します。

- `argparse` でコマンドライン引数を受け取る
- `csv.DictReader` でCSVを辞書として読み込む
- `collections.defaultdict` で商品ごとの合計をためる
- `decimal.Decimal` で売上金額を安全に計算する

最初は「数量 × 単価」ではなく、CSVにすでに売上金額が入っている形にします。これにより、初心者でも処理の流れを追いやすくなります。

壊れにくいCLIにするため、次の点も入れています。

- ファイルが存在しない場合は、分かりやすいエラーメッセージを出す
- 売上金額が数値でない行は、無視せずエラーにする
- 文字コードを `--encoding` で指定できるようにする
- 出力形式を `--format text` または `--format json` で選べるようにする
- CSV読み込み、集計、表示、CLIの入口を関数で分ける
- `pytest` で正常系と異常系をテストする
- `ruff` でコードの基本的な問題をチェックする
- GitHub Actionsでpush時にテストとlintを自動実行する

## 3. ファイル構成

```text
.
├── .github
│   └── workflows
│       └── ci.yml
├── README.md
├── pyproject.toml
├── setup.cfg
├── sales_summary.py
├── data
│   └── sample_sales.csv
└── tests
    └── test_sales_summary.py
```

各ファイルの役割は次の通りです。

- `README.md`: このCLIツールの目的、使い方、設計メモを説明するファイルです。
- `pyproject.toml`: Pythonプロジェクトの設定ファイルです。ビルド設定、pytest設定、ruff設定をまとめて管理します。
- `setup.cfg`: プロジェクト名、Pythonバージョン、開発用依存関係を管理します。古いpipでも `".[dev]"` を読みやすくするために置いています。
- `sales_summary.py`: CLIツール本体です。CSVを読み込み、商品別に売上を合計し、結果を表示します。
- `data/sample_sales.csv`: 動作確認用のサンプルCSVです。
- `tests/test_sales_summary.py`: `pytest` で実行するテストです。正しいCSVを集計できるか、不正なCSVでエラーになるかを確認します。
- `.github/workflows/ci.yml`: GitHub Actionsの設定ファイルです。GitHubへpushしたときにテストとlintを自動実行します。

## セットアップ

最初に仮想環境を作ります。仮想環境を使うと、このプロジェクト用のPythonパッケージを他のプロジェクトと分けて管理できます。

```bash
python3 -m venv .venv
source .venv/bin/activate
```

次に、開発用の依存関係をインストールします。

```bash
python3 -m pip install ".[dev]"
```

ここでインストールされる主な開発ツールは次の2つです。

- `pytest`: テストを実行するためのツールです。
- `ruff`: コードの書き方や単純なミスをチェックするためのツールです。

`".[dev]"` は、「このプロジェクトと、`dev` に書いた開発用依存関係をまとめて入れる」という意味です。

## 4. 実装

実行例:

```bash
python3 sales_summary.py data/sample_sales.csv
```

出力例:

```text
商品別 合計売上
----------------
みかん: 1,500円
りんご: 2,100円
バナナ: 800円
```

列名を変えたい場合は、オプションで指定できます。

```bash
python3 sales_summary.py data/sample_sales.csv --product-column product --sales-column sales
```

文字コードを指定したい場合は、`--encoding` を使います。

```bash
python3 sales_summary.py data/sample_sales.csv --encoding utf-8
```

JSONで出力したい場合は、`--format json` を使います。

```bash
python3 sales_summary.py data/sample_sales.csv --format json
```

出力例:

```json
{"みかん": 1500, "りんご": 2100, "バナナ": 800}
```

主な関数の役割は次の通りです。

- `parse_args()`: コマンドライン引数を読み取ります。
- `read_sales_rows()`: CSVファイルを読み込み、必要な列や売上金額の形式をチェックします。
- `summarize_sales()`: 読み込んだ行を商品別に合計します。
- `format_totals()`: 合計結果を表示用の文字列にします。
- `format_totals_json()`: 合計結果をJSON文字列にします。
- `decimal_to_json_value()`: `Decimal` の合計金額をJSONに入れられる値へ変換します。整数なら数値、小数なら精度を落とさないため文字列にします。
- `print_totals()`: 表示用の文字列をターミナルに出力します。
- `main()`: CLI全体の入口です。エラー表示と終了コードの制御を担当します。

初心者向けのポイントは、「1つの関数に全部書かない」ことです。CSVを読む処理と、集計する処理と、画面に出す処理を分けると、あとから直しやすく、テストもしやすくなります。

`--format json` を追加しても、CSV読み込みや集計の関数は変えていません。出力形式だけを切り替えたいので、変更範囲を表示まわりに寄せています。これにより、既存のtext出力を壊しにくくなります。

テストは次のコマンドで実行します。

```bash
python3 -m pytest
```

lintは次のコマンドで実行します。

```bash
python3 -m ruff check .
```

テストとlintの違いは次の通りです。

- テスト: 入力に対して期待した結果が返るかを確認します。
- lint: import順、未使用の変数、基本的な書き方の問題などを確認します。

GitHub Actionsでは、GitHubへpushしたときに次の2つが自動で実行されます。

```bash
python3 -m pytest
python3 -m ruff check .
```

手元で同じコマンドを実行しておくと、GitHub上で失敗する前に問題を見つけやすくなります。

## 5. テストデータ

`data/sample_sales.csv` には次のようなデータが入っています。

```csv
product,sales
りんご,1200
みかん,800
りんご,900
バナナ,500
みかん,700
バナナ,300
```

同じ商品が複数回出てくるため、商品別の合計処理を確認できます。

## 6. 想定されるバグや改善点

想定されるバグ:

- CSVに `product` や `sales` の列がない
- 売上金額に `abc` のような数値ではない文字が入っている
- 商品名が空になっている
- CSVの文字コードがUTF-8ではない

改善点:

- `quantity` と `unit_price` から売上金額を計算する
- 結果をCSVファイルとして出力する
- 商品名順ではなく売上金額の多い順に並べる
- CLIの標準出力と標準エラー出力も自動テストする
- JSON出力時の小数の扱いを仕様として明確にする
- 小数や通貨記号の扱いをより厳密にする
