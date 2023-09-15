#!/bin/sh

# 检查系统上是否安装了Python 3
if command -v python3 &>/dev/null; then
    python3 watermark.py $@
# 检查系统上是否安装了Python 2
elif command -v python &>/dev/null; then
    python watermark.py $@
else
    echo "未找到Python解释器，请安装Python。"
fi