# macOS / Linux 的统一入口；Windows 开发命令见 README.md。
# 评审环境从仓库根目录执行三条 make 命令即可完成安装、重建和启动。

PYTHON ?= python3.12
BACKEND_PY := starter/.venv/bin/python
PORT ?= 8000

.PHONY: setup rebuild run test

setup:          ## 创建 Python 3.12 环境，并安装后端与前端依赖
	$(PYTHON) -m venv starter/.venv
	$(BACKEND_PY) -m pip install -r starter/requirements.txt
	npm --prefix frontend ci

rebuild:        ## 按 KB-001 规则重建清洗数据库与知识索引
	cd starter && .venv/bin/python -m kbqa.rebuild

run:            ## 构建看板并由 FastAPI 在同一端口提供页面与 API
	npm --prefix frontend run build
	cd starter && .venv/bin/python -m uvicorn kbqa.server:app --host 127.0.0.1 --port $(PORT)

test:           ## 后端回归测试 + 前端类型检查与生产构建
	cd starter && .venv/bin/python -m pytest tests -q
	npm --prefix frontend run build
