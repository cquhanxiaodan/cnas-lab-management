# CNAS 实验室文件管理系统

基于 FastAPI + Vue 3 的 CNAS 实验室管理体系文件管理系统，涵盖人员、设备、质量活动、检测业务、文件管理及不符合项等模块。

## Docker 一键启动

```bash
docker compose up -d --build
```

启动后访问 http://localhost:8000

## 默认账号

- 用户名: `admin`
- 密码: `admin123`

## API 文档

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 数据持久化

SQLite 数据库文件和上传文件通过 Docker Volume 持久化存储，容器重建后数据不会丢失。

## 常用命令

```bash
# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f

# 停止服务
docker compose down

# 重建并启动
docker compose up -d --build
```
