#!/usr/bin/env python3
import argparse
import csv
import json
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="CSVの売上データを読み込み、商品別の合計売上を表示します。"
    )
    parser.add_argument("csv_file", help="読み込むCSVファイルのパス")
    parser.add_argument(
        "--product-column",
        default="product",
        help="商品名が入っている列名。既定値: product",
    )
    parser.add_argument(
        "--sales-column",
        default="sales",
        help="売上金額が入っている列名。既定値: sales",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="CSVファイルの文字コード。既定値: utf-8",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="出力形式。text または json。既定値: text",
    )
    parser.add_argument(
        "--sort",
        choices=["product", "sales"],
        default="product",
        help="並び順。product は商品名順、sales は売上の高い順。既定値: product",
    )
    return parser.parse_args(argv)


def read_sales_rows(
    csv_file,
    product_column="product",
    sales_column="sales",
    encoding="utf-8",
):
    path = Path(csv_file)
    if not path.exists():
        raise FileNotFoundError(f"CSVファイルが見つかりません: {path}")
    if path.is_dir():
        raise ValueError(f"CSVファイルではなくディレクトリが指定されました: {path}")

    rows = []
    try:
        with path.open(newline="", encoding=encoding) as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError("CSVにヘッダー行がありません。")

            missing_columns = [
                column
                for column in (product_column, sales_column)
                if column not in reader.fieldnames
            ]
            if missing_columns:
                raise ValueError(
                    f"CSVに必要な列がありません: {', '.join(missing_columns)}"
                )

            for line_number, row in enumerate(reader, start=2):
                product = row[product_column].strip()
                sales_text = row[sales_column].strip()

                if not product:
                    raise ValueError(f"{line_number}行目の商品名が空です。")

                try:
                    sales = Decimal(sales_text)
                except InvalidOperation as error:
                    raise ValueError(
                        f"{line_number}行目の売上金額が数値ではありません: {sales_text}"
                    ) from error

                rows.append((product, sales))
    except UnicodeDecodeError as error:
        raise ValueError(
            f"CSVファイルの文字コードが {encoding} として読み取れません: {path}"
        ) from error

    return rows


def summarize_sales(rows):
    totals = defaultdict(Decimal)

    for product, sales in rows:
        totals[product] += sales

    return dict(totals)


def sort_totals(totals, sort_by="product"):
    if sort_by == "sales":
        return sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    return sorted(totals.items())


def format_totals(totals, sort_by="product"):
    lines = ["商品別 合計売上", "----------------"]

    for product, total in sort_totals(totals, sort_by):
        lines.append(f"{product}: {total:,}円")

    return "\n".join(lines)


def format_totals_json(totals, sort_by="product"):
    json_ready_totals = {
        product: decimal_to_json_value(total)
        for product, total in sort_totals(totals, sort_by)
    }
    return json.dumps(json_ready_totals, ensure_ascii=False)


def decimal_to_json_value(value):
    if value == value.to_integral_value():
        return int(value)
    return str(value)


def print_totals(totals, sort_by="product"):
    print(format_totals(totals, sort_by))


def main(argv=None):
    args = parse_args(argv)

    try:
        rows = read_sales_rows(
            args.csv_file,
            args.product_column,
            args.sales_column,
            args.encoding,
        )
        totals = summarize_sales(rows)
    except (FileNotFoundError, ValueError) as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(format_totals_json(totals, args.sort))
    else:
        print_totals(totals, args.sort)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
