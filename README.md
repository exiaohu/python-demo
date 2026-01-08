# Python 微服务模版 (Python Demo Playground)

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

一个生产就绪的 Python 微服务模版，基于现代最佳实践和工具构建。

## ✨ 特性

*   **FastAPI**: 高性能，易于学习，快速编码，生产就绪。
*   **异步 SQLAlchemy**: 全异步数据库支持，开发环境使用 `aiosqlite`，生产环境使用 `asyncpg`。
*   **架构**: 清晰的分层架构 (`app/crud`, `app/schemas`, `app/models`)。
*   **数据库迁移**: 集成 **Alembic** 用于自动数据库架构迁移。
*   **安全性**: JWT 身份认证，密码哈希 (Bcrypt)，兼容 OAuth2。支持用户注册、登录及权限管理。
    *   **安全加固**: 强制密钥配置，HTTP Host 头保护 (`TrustedHost`)。
*   **性能**:
    *   **响应缓存**: 针对高频读接口 (如 `/items/`) 集成了 **Redis** 缓存 (`fastapi-cache2`)，显著降低数据库压力。
    *   **极速 JSON**: 使用 `orjson` 替代标准库，大幅提升序列化速度。
    *   **Gzip 压缩**: 自动压缩响应数据，减少网络传输。
    *   **连接池**: 优化的数据库连接池配置。
*   **限流**: 基于 **Redis** (生产) 或内存 (开发) 的 API 速率限制 (`slowapi`)，防止滥用。
*   **动态配置**: 集成 `watchdog` 监听 `.env` 文件变更，支持运行时热加载配置（适用于 Feature Flags 等运行时读取的配置）。
*   **可观测性**: 
    *   **Prometheus 指标**: 内置 `/metrics` 端点用于监控。
    *   **结构化日志**: 使用 `structlog` 的 JSON 日志，包含 **Request ID** 追踪。
*   **Docker & Compose**: 生产优化的多阶段构建 Dockerfile 和一键式 `docker-compose` 部署 (包含 **Redis**)，包含健康检查与网络隔离。
*   **代码质量**: 使用 **Ruff** 进行完整的代码检查和格式化，**Mypy** 进行静态类型检查。
*   **CI/CD**: 集成 GitHub Actions 进行自动化测试和质量门禁，优化的缓存策略。
*   **测试**: 使用 `pytest` 和 `httpx` 的异步测试设置。
*   **标准化 API**: 统一的响应结构 (`data`, `message`) 和分页支持。

## 🏗 项目结构

```text
├── app/
│   ├── api/              # API 路由 (支持版本控制)
│   ├── core/             # 核心配置, 日志, 异常处理
│   ├── crud/             # 数据库 CRUD 操作
│   ├── db/               # 数据库连接 & 会话管理
│   ├── middleware/       # 自定义中间件 (Prometheus, RequestID)
│   ├── models/           # SQLAlchemy ORM 模型
│   ├── schemas/          # Pydantic Schemas (请求/响应)
│   └── main.py           # 应用入口
├── migrations/           # Alembic 数据库迁移脚本
├── tests/                # 异步测试用例
├── .github/              # GitHub Actions CI/CD 配置
├── docker-compose.yml    # 本地开发 / 生产环境编排
├── Dockerfile            # 多阶段构建文件
├── Makefile              # 常用命令快捷方式
└── requirements.txt      # 项目依赖
```

## 🚀 快速开始

### 前置要求

*   Python 3.12+
*   Docker & Docker Compose (可选，推荐)

### 本地开发

1.  **设置环境**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    make install-deps
    ```

2.  **配置**

    ```bash
    cp .env.example .env
    ```

3.  **运行服务器**

    ```bash
    make dev
    ```
    访问: http://localhost:8080/docs

### 🐳 Docker Compose (推荐)

启动完整技术栈 (App + PostgreSQL):

```bash
docker-compose up -d
```

### 🗄 数据库迁移

```bash
# 修改模型后生成新的迁移脚本
make migrate msg="add_user_table"

# 应用迁移到数据库
make migrate-up
```

### 🧪 测试

```bash
make test
```

## 🛠 Makefile 命令

| 命令 | 描述 |
|---------|-------------|
| `make dev` | 启动开发服务器 (带热重载) |
| `make run` | 启动生产服务器 |
| `make test` | 运行异步测试 |
| `make lint` | 运行 Ruff 代码检查和 Mypy 类型检查 |
| `make fmt` | 运行 Ruff 代码格式化 |
| `make clean` | 清理临时文件 |
| `make help` | 查看帮助信息 |
| `make migrate msg="..."` | 生成新的数据库迁移脚本 |
| `make migrate-up` | 应用迁移到数据库 |
| `make migrate-down` | 回滚上一次迁移 |
| `make install-deps` | 安装项目依赖 |

## 📊 API 响应格式

所有 API 响应遵循标准格式:

```json
{
  "data": { ... },
  "message": "Success"
}
```

## 📄 许可证

MIT License
