# 部署指南

本文档介绍如何部署和运行 GomokuAgent 项目。

## 环境要求

### 必需环境

| 软件 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 后端运行环境 |
| Node.js | 18+ | 前端构建环境 |
| uv | 0.12+ | Python 包管理器 |

### 可选环境

| 软件 | 版本 | 说明 |
|------|------|------|
| Git | 2.30+ | 版本控制 |
| npm | 9+ | Node.js 包管理器 |

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/AK993/GomokuAgent.git
cd GomokuAgent
```

### 2. 配置 API Key

创建 `.env` 文件：

```bash
# Windows
echo. > .env

# Linux/Mac
touch .env
```

编辑 `.env` 文件，添加 API Key：

```env
# DeepSeek API (推荐)
DEEPSEEK_API_KEY=sk-your-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL_NAME=deepseek-chat

# 或者 Mimo API
MIMO_API_KEY=sk-your-key-here
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
MIMO_MODEL_NAME=mimo-v2.5
```

### 3. 启动后端

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
uv pip install -e .

# 启动后端服务
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 http://localhost:8000 启动

API 文档：http://localhost:8000/docs

### 4. 启动前端

```bash
# 新终端
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动

## 详细配置

### Python 环境配置

#### 使用 uv（推荐）

```bash
# 安装 uv
pip install uv

# 创建虚拟环境
uv venv

# 激活虚拟环境
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 安装项目
uv pip install -e .
```

#### 使用 pip

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -e .
```

### Node.js 环境配置

```bash
cd frontend

# 安装依赖
npm install

# 或者使用 yarn
yarn install

# 或者使用 pnpm
pnpm install
```

### API Key 配置

#### DeepSeek API

1. 访问 https://platform.deepseek.com
2. 注册并登录
3. 创建 API Key
4. 复制到 `.env` 文件

```env
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL_NAME=deepseek-chat
```

#### Mimo API

1. 访问 https://api.xiaomimimo.com
2. 注册并登录
3. 创建 API Key
4. 复制到 `.env` 文件

```env
MIMO_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
MIMO_BASE_URL=https://api.xiaomimimo.com/v1
MIMO_MODEL_NAME=mimo-v2.5
```

## 启动方式

### 方式 1：手动启动（开发）

```bash
# 终端 1：启动后端
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 终端 2：启动前端
cd frontend
npm run dev
```

### 方式 2：使用 CLI 命令

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 启动服务
gomokuagent
```

### 方式 3：生产部署

#### 构建前端

```bash
cd frontend
npm run build
```

生成的文件在 `frontend/dist/` 目录。

#### 部署后端

```bash
# 使用 gunicorn
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# 或者直接使用 uvicorn
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

#### 配置 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket 支持（可选）
    location /ws/ {
        proxy_pass http://127.0.0.1:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Docker 部署（可选）

### Dockerfile

```dockerfile
# 后端
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv pip install --system -e .

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./memory:/app/memory

  frontend:
    build:
      context: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

## 环境变量

| 变量名 | 必填 | 说明 | 默认值 |
|--------|------|------|--------|
| DEEPSEEK_API_KEY | 是* | DeepSeek API Key | - |
| DEEPSEEK_BASE_URL | 否 | DeepSeek API 地址 | https://api.deepseek.com |
| DEEPSEEK_MODEL_NAME | 否 | 模型名称 | deepseek-chat |
| MIMO_API_KEY | 是* | Mimo API Key | - |
| MIMO_BASE_URL | 否 | Mimo API 地址 | https://api.xiaomimimo.com/v1 |
| MIMO_MODEL_NAME | 否 | 模型名称 | mimo-v2.5 |

*至少需要配置一个 API Key

## 常见问题

### 1. 启动报错：ModuleNotFoundError

```bash
# 确保虚拟环境已激活
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 重新安装依赖
uv pip install -e .
```

### 2. 前端无法连接后端

检查：
- 后端是否启动成功
- 端口是否正确（默认 8000）
- 防火墙是否放行

```bash
# 检查后端是否运行
curl http://localhost:8000/

# 检查端口占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac
```

### 3. API Key 无效

```bash
# 检查 .env 文件
cat .env

# 确认 API Key 格式正确
# DeepSeek: sk-xxxxxxxxxxxxxxxxxxxxxxxx
# Mimo: sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. 内存不足

MCTS 搜索需要一定内存。如果出现内存不足：

```python
# 减少模拟次数
mcts = MCTS(simulations=100)  # 默认 300
```

### 5. 响应速度慢

可能原因：
- API 响应慢
- 模拟次数过多

解决方案：
- 使用更快的 API
- 减少模拟次数
- 使用更快的机器

## 监控和日志

### 查看后端日志

```bash
# 实时查看日志
tail -f logs/app.log

# 或者直接查看 uvicorn 输出
```

### 性能监控

```bash
# 查看内存使用
ps aux | grep uvicorn

# 查看 CPU 使用
top -p $(pgrep -f uvicorn)
```

## 备份和恢复

### 备份

```bash
# 备份记忆数据
cp memory/games.json memory/games.json.backup

# 备份配置
cp .env .env.backup
```

### 恢复

```bash
# 恢复记忆数据
cp memory/games.json.backup memory/games.json

# 恢复配置
cp .env.backup .env
```

## 更新

```bash
# 拉取最新代码
git pull

# 更新依赖
uv pip install -e .

# 重启服务
```
