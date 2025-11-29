#!/bin/bash

# 获取脚本所在目录（兼容性更好的写法）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 切换到脚本所在目录
cd "$SCRIPT_DIR"

# 检查 app_ui.py 文件是否存在
if [ ! -f "app_ui.py" ]; then
    echo "错误: app_ui.py 文件未找到"
    exit 1
fi

# 以管理员权限运行 app_ui.py
sudo python app_ui.py