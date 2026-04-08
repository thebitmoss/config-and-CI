import json
from decimal import Decimal

import pytest

from sales_summary import main, read_sales_rows, summarize_sales


def test_summarize_sales_success(tmp_path):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "product,sales\n"
        "りんご,1200\n"
        "みかん,800\n"
        "りんご,900\n",
        encoding="utf-8",
    )

    rows = read_sales_rows(csv_file)
    totals = summarize_sales(rows)

    assert totals == {
        "りんご": Decimal("2100"),
        "みかん": Decimal("800"),
    }


def test_read_sales_rows_raises_when_file_missing(tmp_path):
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="CSVファイルが見つかりません"):
        read_sales_rows(missing_file)


def test_read_sales_rows_raises_when_sales_is_invalid(tmp_path):
    csv_file = tmp_path / "invalid_sales.csv"
    csv_file.write_text(
        "product,sales\n"
        "りんご,abc\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="2行目の売上金額が数値ではありません"):
        read_sales_rows(csv_file)


def test_main_outputs_json_when_format_is_json(tmp_path, capsys):
    csv_file = tmp_path / "sales.csv"
    csv_file.write_text(
        "product,sales\n"
        "りんご,1200\n"
        "みかん,800\n"
        "りんご,900\n",
        encoding="utf-8",
    )

    exit_code = main([str(csv_file), "--format", "json"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert json.loads(captured.out) == {
        "みかん": 800,
        "りんご": 2100,
    }
    assert captured.err == ""
