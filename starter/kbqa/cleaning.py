"""把原始 sales 导进 var/clean.db，指标都查这张表。"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Optional

#: 金额里的 `¥` 去掉再按数字解析。
_CURRENCY = str.maketrans("", "", "¥￥ \t　")

REMOVAL_REASONS = (
    "1_unparseable_date",
    "2_empty_amount",
    "3_qty_le_zero",
    "4_store_not_in_stores",
    "5_product_not_in_products",
    "6_duplicate_row",
)


def parse_amount(value: Optional[str]) -> tuple[Optional[int], str]:
    """返回 (分, 状态)。状态取值：`ok`、`empty`、`bad`。

    KB-001 §2.3 与 §3.2：`¥38.00` 与 `38.00` 是同一个金额；空金额直接剔除，**不回填**。
    """
    text = (value or "").translate(_CURRENCY)
    if not text:
        return None, "empty"
    try:
        cents = int((Decimal(text) * 100).to_integral_value())
    except (InvalidOperation, ValueError):
        return None, "bad"
    return cents, "ok"


def parse_qty(value: Optional[str]) -> Optional[int]:
    """KB-001 §2.4：只接受数学意义上的整数。

    旧实现使用 ``int(Decimal(text))``，会把 ``1.5`` 静默截断成 ``1``，从而制造
    并不存在的销量。这里先检查 Decimal 是否等于其整数值，再进行转换。
    """
    text = (value or "").strip()
    if not text:
        return None
    try:
        number = Decimal(text)
    except (InvalidOperation, ValueError):
        return None
    if not number.is_finite() or number != number.to_integral_value():
        return None
    return int(number)


def parse_date(value: Optional[str]) -> Optional[str]:
    """把 KB-001 允许的三种日期格式统一成 ISO ``YYYY-MM-DD``。

    SQLite 中日期以文本保存；只有全部转为 ISO 格式后，字符串范围比较以及
    ``MIN``/``MAX`` 才与真实日期顺序一致。第三种格式明确是日在前、月在后，
    不能按美式月日在前解析。
    """

    text = (value or "").strip()
    if not text:
        return None
    for pattern in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue
    return None


@dataclass
class CleaningReport:
    raw_rows: int = 0
    kept_rows: int = 0
    kept_sales_rows: int = 0
    kept_refund_rows: int = 0
    removed: dict[str, int] = field(default_factory=lambda: {k: 0 for k in REMOVAL_REASONS})
    note_unparseable_amount: int = 0

    def as_dict(self) -> dict:
        return {
            "raw_rows": self.raw_rows,
            "removed": dict(self.removed, note_unparseable_amount=self.note_unparseable_amount),
            "kept_rows": self.kept_rows,
            "kept_sales_rows": self.kept_sales_rows,
            "kept_refund_rows": self.kept_refund_rows,
        }


def open_readonly(path: Path) -> sqlite3.Connection:
    """以 SQLite 只读模式打开数据库，避免查询代码意外改写源数据。"""

    uri = "file:%s?mode=ro" % path.resolve().as_posix()
    conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def clean_rows(
    rows: Iterable[sqlite3.Row],
    *,
    valid_store_ids: set[str],
    valid_product_ids: set[str],
) -> tuple[list[tuple], CleaningReport]:
    """按 KB-001 §2、§3 的固定顺序规范化并剔除销售明细。

    旧实现没有真正清洗，而是把每一行原样追加到 ``kept``，仅把无法解析的
    金额和数量改成 0。那会让错误行继续参与订单数、销量和日期范围计算。

    删除原因必须按制度顺序判断：一行同时有多个问题时，只归入最先命中的
    原因。重复判断则必须放在所有字段规范化之后，否则大小写或日期写法不同
    的同一行无法被识别。
    """

    report = CleaningReport()
    kept: list[tuple] = []
    seen: set[tuple] = set()
    for row in rows:
        report.raw_rows += 1

        normalized_date = parse_date(row["date"])
        if normalized_date is None:
            report.removed["1_unparseable_date"] += 1
            continue

        cents, status = parse_amount(row["amount"])
        if status != "ok" or cents is None:
            # 当前数据里的 150 条都是空金额。若隐藏数据出现非空乱码，也不能
            # 伪造为 0 元继续统计；额外计数方便数据质量面板暴露这种情况。
            report.removed["2_empty_amount"] += 1
            if status == "bad":
                report.note_unparseable_amount += 1
            continue

        qty = parse_qty(row["qty"])
        if qty is None or qty <= 0:
            report.removed["3_qty_le_zero"] += 1
            continue

        store_id = (row["store_id"] or "").strip().upper()
        if store_id not in valid_store_ids:
            report.removed["4_store_not_in_stores"] += 1
            continue

        product_id = (row["product_id"] or "").strip().upper()
        if product_id not in valid_product_ids:
            report.removed["5_product_not_in_products"] += 1
            continue

        normalized = (
            (row["order_id"] or "").strip(),
            normalized_date,
            store_id,
            product_id,
            qty,
            cents,
            (row["payment"] or "").strip(),
        )

        if normalized in seen:
            report.removed["6_duplicate_row"] += 1
            continue
        seen.add(normalized)

        # ``is_refund`` 是查询优化字段，不参与重复判断；退款的定义完全由
        # 规范化后的 amount < 0 决定。
        kept.append(normalized + (1 if cents < 0 else 0,))

    report.kept_rows = len(kept)
    report.kept_sales_rows = sum(1 for row in kept if row[5] > 0)
    report.kept_refund_rows = sum(1 for row in kept if row[5] < 0)
    return kept, report


_SCHEMA = """
CREATE TABLE stores (store_id TEXT PRIMARY KEY, store_name TEXT, category TEXT, district TEXT);
CREATE TABLE products (product_id TEXT PRIMARY KEY, product_name TEXT,
                       product_category TEXT, unit_price REAL);
CREATE TABLE sales_clean (
    order_id TEXT, date TEXT, store_id TEXT, product_id TEXT,
    qty INTEGER, amount_cents INTEGER, payment TEXT, is_refund INTEGER
);
CREATE INDEX idx_clean_date ON sales_clean(date);
CREATE INDEX idx_clean_store ON sales_clean(store_id);
CREATE INDEX idx_clean_product ON sales_clean(product_id);
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
"""


def build_clean_db(source: Path, target: Path) -> CleaningReport:
    """从只读的源库重建清洗表。返回清洗台账，供 `/api/health` 与数据质量面板使用。"""
    if not source.exists():
        raise FileNotFoundError("找不到源数据库：%s" % source)
    src = open_readonly(source)
    try:
        stores = [tuple(r) for r in src.execute("SELECT store_id, store_name, category, district FROM stores")]
        products = [
            tuple(r)
            for r in src.execute(
                "SELECT product_id, product_name, product_category, unit_price FROM products"
            )
        ]
        rows, report = clean_rows(
            src.execute("SELECT order_id, date, store_id, product_id, qty, amount, payment FROM sales"),
            valid_store_ids={str(row[0]).strip().upper() for row in stores},
            valid_product_ids={str(row[0]).strip().upper() for row in products},
        )
    finally:
        src.close()

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    out = sqlite3.connect(target)
    try:
        out.executescript(_SCHEMA)
        out.executemany("INSERT INTO stores VALUES (?,?,?,?)", stores)
        out.executemany("INSERT INTO products VALUES (?,?,?,?)", products)
        out.executemany("INSERT INTO sales_clean VALUES (?,?,?,?,?,?,?,?)", rows)
        out.execute(
            "INSERT INTO meta VALUES ('cleaning_report', ?)",
            (json.dumps(report.as_dict(), ensure_ascii=False),),
        )
        out.execute("INSERT INTO meta VALUES ('source_db', ?)", (source.name,))
        out.commit()
    finally:
        out.close()
    return report
