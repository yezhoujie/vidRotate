# 视频旋转器 vidRotate

一个跨平台（macOS/Linux/Windows）的命令行批量视频旋转工具（将视频向左/向右旋转 90 度），支持自动检测方向、格式转换、灵活参数、自动检测/安装 ffmpeg，并支持 GPU 加速、码率控制、多平台一键打包。

## 特性

- 支持批量/单文件旋转，自动检测竖屏视频并旋转
- 支持多种主流格式（mp4, avi, mkv, mov, flv, wmv）及格式互转
- 输出路径可为目录或文件名，自动判断
- 自动检测 ffmpeg，缺失时自动安装（支持 Homebrew/apt/Windows 自动下载）
- 依赖极少
- 支持 `--gpu` 参数，自动检测并优先启用 GPU 加速（NVIDIA NVENC、macOS VideoToolbox），大幅提升转码速度
- GPU 加速时限制码率，避免体积暴增，适合大多数高清视频场景
- 可执行文件支持 Windows（x86_64/ARM64）、macOS（Intel/Apple Silicon）、Linux（x86_64/ARM64）多平台一键打包

## 安装依赖

```bash
python3 -m venv .venv  # 推荐使用虚拟环境
source .venv/bin/activate
pip3 install -r requirements.txt
```

## 使用方法

```bash
python3 vidrotate.py -f <输入文件/文件夹> -o <输出文件/文件夹> -d <方向: left|right|auto> --format <输出格式> [--gpu] [-v]
```

- 支持的视频格式：mp4, avi, mkv, mov, flv, wmv
- 旋转方向：
  - left（逆时针 90°）
  - right（顺时针 90°）
  - auto（自动检测，竖屏转横屏，横屏跳过）
- 输出文件名格式：原文件名\_fixed.后缀名（批量时）
- -o 可为输出目录或单个输出文件名（仅单文件时）
- --format 指定输出格式（如 mp4/avi），默认与输入一致
- --gpu 启用 GPU 加速（如支持，自动加码率限制）
- -v/--verbose 显示 ffmpeg 详细日志

## 常用参数说明

- `--gpu`：如支持则启用 GPU 加速（NVIDIA/Apple Silicon），大幅提升转码速度，自动加码率限制。
- `-d/--direction`：旋转方向，支持 left/right/auto。
- `-f/--file`、`-o/--output`：输入/输出文件或目录。
- `--format`：输出格式，默认与输入一致。
- `-v/--verbose`：显示 ffmpeg 详细日志。

## 构建 all-in-one 可执行文件

```bash
pip3 install pyinstaller
./build.sh
```

- 支持主流平台和芯片，详见 [build.sh](build.sh) 和 CI/CD。
- 可执行文件产物位于 `dist/` 目录，命名规则如：
  - `vidrotate_win_x86_64.exe`、`vidrotate_win_arm64.exe`
  - `vidrotate_mac_x86_64`、`vidrotate_mac_arm64`
  - `vidrotate_linux_x86_64`、`vidrotate_linux_arm64`

## 直接下载可执行文件使用

[从 release 下载](https://github.com/yezhoujie/vidRotate/releases)

## 依赖

- Python 3.x
- tqdm（已在 requirements.txt，无需手动安装）
- ffmpeg（自动检测/安装，需本地可用 ffmpeg 命令行工具）

## 常见问题

- 如遇 pip3 安装权限问题，优先使用虚拟环境
- Windows 下首次自动下载 ffmpeg，需要手动配置 path， 然后重启终端
- Windows 下运行可执行文件，可能会被杀毒软件误认为病毒，（因为他会从公网自动下载 ffmpeg）,请在杀毒软件中添加信任或排除。
- gpu 加速现只支持 NVIDIA NVENC 和 macOS VideoToolbox，其他平台不好测试，欢迎 PR.
- 启用 gpu 加速时，码率会自动限制为 2M，避免体积暴增，适合大多数高清视频场景。
- N 卡启用 gpu 加速时，可能会报 gpu 接口版本与 ffmpeg 版本不匹配的错误，这是可能需要更新显卡驱动，或者降低 ffmpeg 的版本。

## 查看参数说明

```bash
python3 vidrotate.py -h
```

---

如有问题或建议，欢迎提 issue 或 PR！
