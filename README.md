# 视频旋转器 vidRotate

一个跨平台（macOS/Linux/Windows）的命令行批量视频旋转工具（将视频向左/向右旋转 90 度），支持自动检测方向、格式转换、灵活参数、自动检测/安装 ffmpeg。

## 特性

- 支持批量/单文件旋转，自动检测竖屏视频并旋转
- 支持多种主流格式（mp4, avi, mkv, mov, flv, wmv）及格式互转
- 输出路径可为目录或文件名，自动判断
- 自动检测 ffmpeg，缺失时自动安装（支持 Homebrew/apt/Windows 自动下载）
- 依赖极少

## 安装依赖

```bash
python3 -m venv .venv  # 推荐使用虚拟环境
source .venv/bin/activate
pip3 install -r requirements.txt
```

## 使用方法

```bash
python3 vidrotate.py -f <输入文件/文件夹> -o <输出文件/文件夹> -d <方向: left|right|auto> --format <输出格式> [-v]
```

- 支持的视频格式：mp4, avi, mkv, mov, flv, wmv
- 旋转方向：
  - left（逆时针 90°）
  - right（顺时针 90°）
  - auto（自动检测，竖屏转横屏，横屏跳过）
- 输出文件名格式：原文件名\_fixed.后缀名（批量时）
- -o 可为输出目录或单个输出文件名（仅单文件时）
- --format 指定输出格式（如 mp4/avi），默认与输入一致
- -v/--verbose 显示 ffmpeg 详细日志

## 依赖

- Python 3.x
- tqdm（已在 requirements.txt，无需手动安装）
- ffmpeg（自动检测/安装，需本地可用 ffmpeg 命令行工具）

## 常见问题

- 如遇 pip3 安装权限问题，优先使用虚拟环境
- Windows 下首次自动下载 ffmpeg 后需重启终端

## 查看参数说明

```bash
python3 vidrotate.py -h
```

---

如有问题或建议，欢迎提 issue 或 PR！
