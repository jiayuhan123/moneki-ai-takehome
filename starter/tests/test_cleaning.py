"""KB-001 v3 数据清洗规则的回归测试。

这些测试刻意从业务口径出发，而不是复刻 ``cleaning.py`` 的实现细节。
这样后续即使重构清洗管线，只要产物仍符合 KB-001，测试就不需要跟着改。
"""

from __future__ import annotations

from kbqa.cleaning import clean_rows


VALID_STORES = {"S01", "S02"}
VALID_PRODUCTS = {"P01", "P02"}


def sale(**overrides):
    """构造一条最小合法销售明细，单个测试只覆盖自己关心的字段。"""

    row = {
        "order_id": "ORD-001",
        "date": "2026-06-07",
        "store_id": "S01",
        "product_id": "P01",
        "qty": "2",
        "amount": "38.00",
        "payment": "微信",
    }
    row.update(overrides)
    return row


def clean(rows):
    """所有测试使用相同的维表集合，确保先规范化、再校验外键。"""

    return clean_rows(rows, valid_store_ids=VALID_STORES, valid_product_ids=VALID_PRODUCTS)


def test_clean_rows_normalizes_supported_fields():
    rows = [
        sale(order_id="ORD-ISO", date="2026-06-07"),
        sale(order_id="ORD-SLASH", date="2026/6/8", store_id=" s01 "),
        sale(
            order_id="ORD-LEGACY",
            date="09-06-2026",
            product_id=" p02 ",
            amount=" ￥42.00 ",
        ),
    ]

    cleaned, report = clean(rows)

    assert [row[1] for row in cleaned] == ["2026-06-07", "2026-06-08", "2026-06-09"]
    assert cleaned[1][2] == "S01"
    assert cleaned[2][3] == "P02"
    assert cleaned[2][5] == 4200
    assert report.kept_rows == 3


def test_clean_rows_applies_removal_rules_in_declared_order():
    duplicate = sale(order_id="ORD-DUP")
    rows = [
        sale(order_id="ORD-BAD-DATE", date="N/A"),
        sale(order_id="ORD-NO-AMOUNT", amount=""),
        sale(order_id="ORD-BAD-QTY", qty="0"),
        sale(order_id="ORD-BAD-STORE", store_id="S99"),
        sale(order_id="ORD-BAD-PRODUCT", product_id="P99"),
        duplicate,
        dict(duplicate),
    ]

    cleaned, report = clean(rows)

    assert len(cleaned) == 1
    assert report.as_dict() == {
        "raw_rows": 7,
        "removed": {
            "1_unparseable_date": 1,
            "2_empty_amount": 1,
            "3_qty_le_zero": 1,
            "4_store_not_in_stores": 1,
            "5_product_not_in_products": 1,
            "6_duplicate_row": 1,
            "note_unparseable_amount": 0,
        },
        "kept_rows": 1,
        "kept_sales_rows": 1,
        "kept_refund_rows": 0,
    }


def test_clean_rows_keeps_distinct_products_in_one_order():
    """共享 order_id 不是重复；只有七个规范化字段全相同才删除。"""

    rows = [
        sale(order_id="ORD-MULTI", product_id="P01"),
        sale(order_id="ORD-MULTI", product_id="P02", amount="42.00"),
    ]

    cleaned, report = clean(rows)

    assert len(cleaned) == 2
    assert report.removed["6_duplicate_row"] == 0


def test_clean_rows_rejects_fractional_quantity_instead_of_truncating_it():
    """“按整数解析”不能把 1.5 静默截断成 1，否则会制造虚假销量。"""

    cleaned, report = clean([sale(qty="1.5")])

    assert cleaned == []
    assert report.removed["3_qty_le_zero"] == 1
