#!/bin/bash
# build.sh: 自动检测当前平台和芯片类型，使用 PyInstaller 打包 vidrotate.py 为本机可用的可执行文件
set -e

PY_FILE="vidrotate.py"
APP_NAME="vidrotate"

# 检查 pyinstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "未检测到 pyinstaller，正在安装..."
    pip install pyinstaller
fi

PLATFORM="$(uname -s)"
ARCH="$(uname -m)"

echo "当前平台: $PLATFORM"
echo "当前架构: $ARCH"

if [[ "$PLATFORM" == "Darwin" ]]; then
    if [[ "$ARCH" == "arm64" ]]; then
        echo "正在为 macOS ARM (Apple Silicon) 构建..."
        pyinstaller --onefile --name ${APP_NAME}_mac_arm64 $PY_FILE
    else
        echo "正在为 macOS Intel 构建..."
        pyinstaller --onefile --name ${APP_NAME}_mac_x86_64 $PY_FILE
    fi
elif [[ "$PLATFORM" == "Linux" ]]; then
    if [[ "$ARCH" == "aarch64" ]]; then
        echo "正在为 Linux ARM64 构建..."
        pyinstaller --onefile --name ${APP_NAME}_linux_arm64 $PY_FILE
    else
        echo "正在为 Linux x86_64 构建..."
        pyinstaller --onefile --name ${APP_NAME}_linux_x86_64 $PY_FILE
    fi
elif [[ "$PLATFORM" =~ MINGW|MSYS|CYGWIN|Windows_NT ]]; then
    if [[ "$ARCH" == "ARM64" || "$ARCH" == "aarch64" ]]; then
        echo "正在为 Windows ARM64 构建..."
        pyinstaller --onefile --name ${APP_NAME}_win_arm64.exe $PY_FILE
    else
        echo "正在为 Windows x86_64 构建..."
        pyinstaller --onefile --name ${APP_NAME}_win_x86_64.exe $PY_FILE
    fi
else
    echo "不支持的平台: $PLATFORM $ARCH"
    exit 1
fi

echo -e "\n打包完成！可执行文件位于 dist/ 目录下。"
echo "如需其它平台产物，请在目标平台或用 CI/CD 分别运行本脚本。"
