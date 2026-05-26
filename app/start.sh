#!/bin/bash
# 遇到错误就退出
set -e

echo "🚀 Step 1: 初始化 Docker 内的数据库（建表 + 插初始数据）..."
python database.py
python insert_data.py

echo "🔄 Step 2: 启动数据同步服务（同步到 VM）..."
# 这里的 -u 是为了让 Python 日志实时输出，不被 bash 缓存
python -u sync_to_vm.py