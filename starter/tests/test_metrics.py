"""指标口径的最小数据库测试。

这里不用生产数据的答案反推实现，而是在临时 SQLite 中放入可人工核算的销售、
多商品订单和退款。这样可以精确指出某个公式错在哪里。
"""

from __future__ import annotations

import sqlite3

from kbqa.tools import DataTools


def metric_tools(tmp_path) -> DataTools:
    db_path = tmp_path / "metrics.db"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE sales_clean (
            order_id TEXT, date TEXT, store_id TEXT, product_id TEXT,
            qty INTEGER, amount_cents INTEGER, payment TEXT, is_refund INTEGER
        );
        CREATE TABLE stores (store_id TEXT PRIMARY KEY, store_name TEXT, category TEXT, district TEXT);
        CREATE TABLE products (product_id TEXT PRIMARY KEY, product_name TEXT,
                               product_category TEXT, unit_price REAL);
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
        """
    )
    conn.executemany(
        "INSERT INTO sales_clean VALUES (?,?,?,?,?,?,?,?)",
        [
            # ORD-1 有两个商品，但有效订单数只能算 1。
            ("ORD-1", "2026-06-18", "S01", "P01", 2, 2000, "微信", 0),
            ("ORD-1", "2026-06-18", "S01", "P02", 1, 1000, "微信", 0),
            ("ORD-2", "2026-06-18", "S01", "P01", 1, 500, "现金", 0),
            # 退款按退款发生日归属：净营业额减 5 元，销量减 1。
            ("REF-1", "2026-06-18", "S01", "P01", 1, -500, "微信", 1),
            # 下一天的数据用于确认 end 是闭区间且不会越界多算。
            ("ORD-3", "2026-06-19", "S01", "P01", 1, 900, "微信", 0),
        ],
    )
    conn.commit()
    conn.close()
    return DataTools(db_path)


def test_summary_uses_kb001_metrics_and_closed_date_range(tmp_path):
    tools = metric_tools(tmp_path)

    result = tools.query_metrics("2026-06-18", "2026-06-18")

    assert result == {
        "start": "2026-06-18",
        "end": "2026-06-18",
        "store_id": None,
        "product_id": None,
        "net_revenue": 30.0,
        "refund_amount": 5.0,
        "orders": 2,
        "aov": 15.0,
        "qty": 3,
    }


def test_summary_empty_range_returns_zero_and_null_aov(tmp_path):
    tools = metric_tools(tmp_path)

    result = tools.query_metrics("2026-07-01", "2026-07-02")

    assert result["net_revenue"] == 0
    assert result["refund_amount"] == 0
    assert result["orders"] == 0
    assert result["qty"] == 0
    assert result["aov"] is None
