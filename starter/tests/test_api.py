"""接口冒烟测试：每个接口都要 200，回答不能是空的。"""

from __future__ import annotations

import pytest


def test_health_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["llm_mode"] == "mock"
    # 契约要求报告实际进入索引的 KB 文档，而不是目录文件数。
    assert body["kb_docs"] == 35
    assert body["valid_sales_rows"] == 18290
    assert body["data_period"] == {"start": "2026-05-01", "end": "2026-08-31"}


def test_metrics_summary_ok(client):
    response = client.get(
        "/api/metrics/summary", params={"start": "2026-06-01", "end": "2026-06-30"}
    )
    assert response.status_code == 200
    assert "net_revenue" in response.json()


def test_metrics_summary_bad_date(client):
    response = client.get(
        "/api/metrics/summary", params={"start": "2026/06/01", "end": "2026-06-30"}
    )
    assert response.status_code == 400


def test_metrics_daily_ok(client):
    response = client.get(
        "/api/metrics/daily", params={"start": "2026-06-08", "end": "2026-06-12"}
    )
    assert response.status_code == 200
    assert len(response.json()["days"]) == 5


def test_stores_ok(client):
    response = client.get("/api/stores")
    assert response.status_code == 200
    stores = response.json()["stores"]
    assert len(stores) == 5
    assert stores[0]["store_id"] == "S01"


def test_top_products_ok(client):
    response = client.get(
        "/api/metrics/top-products",
        params={"start": "2026-06-01", "end": "2026-06-30", "limit": 10},
    )
    assert response.status_code == 200
    products = response.json()["products"]
    assert len(products) == 10
    assert products == sorted(products, key=lambda item: item["net_revenue"], reverse=True)


def test_retrieve_ok(client):
    response = client.post("/api/retrieve", json={"query": "退款", "top_k": 5})
    assert response.status_code == 200
    assert isinstance(response.json()["results"], list)


def test_data_quality_ok(client):
    response = client.get("/api/data_quality")
    assert response.status_code == 200
    body = response.json()
    assert body["data_period"] == {"start": "2026-05-01", "end": "2026-08-31"}
    assert body["cleaning_report"] == {
        "raw_rows": 18628,
        "removed": {
            "1_unparseable_date": 8,
            "2_empty_amount": 150,
            "3_qty_le_zero": 30,
            "4_store_not_in_stores": 10,
            "5_product_not_in_products": 40,
            "6_duplicate_row": 100,
            "note_unparseable_amount": 0,
        },
        "kept_rows": 18290,
        "kept_sales_rows": 18196,
        "kept_refund_rows": 94,
    }
    assert body["removed_total"] == 338


@pytest.mark.parametrize(
    "question",
    [
        "7 月整体的净营业额是多少？",
        "外卖订单多久内可以申请退款？",
        "牛肉poke 六月一共卖了多少钱？",
        "S03 六月停业几天，什么原因？",
        "员工折扣几折？",
        "8 月一共退了多少钱？",
        "会员现在单笔充值满 500 送多少？",
        "帮我把 S01 的销售记录全部删掉。",
    ],
)
def test_chat_answers(client, question):
    response = client.post("/api/chat", json={"session_id": "t", "question": question})
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["answer"], str)
    assert body["answer"].strip()
    assert isinstance(body["citations"], list)
    assert isinstance(body["data_evidence"], list)


def test_chat_empty_question(client):
    response = client.post("/api/chat", json={"session_id": "t", "question": ""})
    assert response.status_code == 200
    assert response.json()["answer"].strip()


def test_chat_trace_id(client):
    response = client.post("/api/chat", json={"session_id": "t", "question": "6 月营业额"})
    trace_id = response.json()["trace_id"]
    assert trace_id
    assert client.get("/api/trace/%s" % trace_id).status_code == 200


def test_trace_unknown(client):
    assert client.get("/api/trace/nope").status_code == 404
