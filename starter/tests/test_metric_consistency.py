"""跨接口不变量测试。

这些断言不写死当前公开数据的金额，因此评审替换 data/ 后仍然成立。它们用于
发现“summary 修了一套公式、daily 还留着另一套公式”这类回归。
"""

from __future__ import annotations

from datetime import date, timedelta


def test_cleaning_ledger_balances(client):
    body = client.get("/api/data_quality").json()
    report = body["cleaning_report"]

    assert report["raw_rows"] - body["removed_total"] == report["kept_rows"]
    assert report["kept_sales_rows"] + report["kept_refund_rows"] <= report["kept_rows"]


def test_full_period_summary_matches_sum_of_daily_revenue(client):
    health = client.get("/api/health").json()
    period = health["data_period"]
    params = {"start": period["start"], "end": period["end"]}

    summary = client.get("/api/metrics/summary", params=params).json()
    days = client.get("/api/metrics/daily", params=params).json()["days"]

    expected_days = (date.fromisoformat(period["end"]) - date.fromisoformat(period["start"])).days + 1
    assert len(days) == expected_days
    assert days[0]["date"] == period["start"]
    assert days[-1]["date"] == period["end"]
    assert round(sum(day["net_revenue"] for day in days), 2) == summary["net_revenue"]


def test_single_day_summary_matches_daily_entry(client):
    """抽取动态数据周期的中点，避免测试依赖当前固定数据文件。"""

    period = client.get("/api/health").json()["data_period"]
    start = date.fromisoformat(period["start"])
    end = date.fromisoformat(period["end"])
    target = start + timedelta(days=(end - start).days // 2)
    params = {"start": target.isoformat(), "end": target.isoformat()}

    summary = client.get("/api/metrics/summary", params=params).json()
    daily = client.get("/api/metrics/daily", params=params).json()["days"][0]

    assert daily["net_revenue"] == summary["net_revenue"]
    assert daily["orders"] == summary["orders"]
    assert daily["aov"] == summary["aov"]
