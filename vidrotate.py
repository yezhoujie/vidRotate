import os
import sys
import argparse
import subprocess
from pathlib import Path
import shutil
import platform
import zipfile
import urllib.request
import tempfile
from tqdm import tqdm  # 依赖由 requirements.txt 管理

# 支持的视频文件扩展名列表
VIDEO_EXTS = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv']

def is_video_file(file_path):
    """
    判断文件是否为支持的视频格式。

    Args:
        file_path (Path): 文件路径对象。

    Returns:
        bool: 是否为支持的视频文件。
    """
    return file_path.suffix.lower() in VIDEO_EXTS

def get_video_files(input_path):
    """
    获取输入路径下所有支持的视频文件。

    Args:
        input_path (str): 输入文件或文件夹路径。

    Returns:
        List[Path]: 支持的视频文件列表。
    """
    p = Path(input_path)
    if p.is_file() and is_video_file(p):
        return [p]
    elif p.is_dir():
        return [f for f in p.iterdir() if f.is_file() and is_video_file(f)]
    else:
        return []

def get_video_orientation(video_path):
    """
    使用 ffprobe 获取视频的宽高，判断横屏或竖屏。

    Args:
        video_path (Path): 视频文件路径。

    Returns:
        str: 'portrait'（竖屏）、'landscape'（横屏）或 'unknown'。
    """
    cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'csv=s=x:p=0', str(video_path)
    ]
    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
        width, height = map(int, output.split('x'))
        if height > width:
            return 'portrait'  # 竖屏
        else:
            return 'landscape'  # 横屏
    except Exception:
        return 'unknown'

def ffmpeg_supports_videotoolbox():
    """
    检查 ffmpeg 是否支持 h264_videotoolbox 编码器。
    """
    try:
        output = subprocess.check_output(['ffmpeg', '-hide_banner', '-encoders'], stderr=subprocess.STDOUT).decode()
        return 'h264_videotoolbox' in output
    except Exception:
        return False

def ffmpeg_supports_nvenc():
    """
    检查 ffmpeg 是否支持 h264_nvenc 编码器（NVIDIA GPU）。
    """
    try:
        output = subprocess.check_output(['ffmpeg', '-hide_banner', '-encoders'], stderr=subprocess.STDOUT).decode()
        return 'h264_nvenc' in output
    except Exception:
        return False

def rotate_video_ffmpeg(input_file, output_file, direction, verbose=False, use_gpu=False):
    """
    使用 ffmpeg 旋转视频。

    Args:
        input_file (Path): 输入视频文件路径。
        output_file (Path): 输出视频文件路径。
        direction (str): 'left'（逆时针90°）或 'right'（顺时针90°）。
        verbose (bool): 是否显示 ffmpeg 日志。
        use_gpu (bool): 是否尝试使用 GPU 加速（macOS VideoToolbox/Windows NVIDIA NVENC）。
    """
    if direction == 'left':
        transpose = '2'  # 逆时针
    else:
        transpose = '1'  # 顺时针
    cmd = [
        'ffmpeg', '-y', '-i', str(input_file), '-vf', f'transpose={transpose}', '-c:a', 'copy'
    ]
    sys_platform = platform.system().lower()
    if use_gpu:
        # 优先用 NVENC（N卡），否则 macOS 用 VideoToolbox，均加码率限制
        if ffmpeg_supports_nvenc():
            cmd += ['-c:v', 'h264_nvenc', '-b:v', '2M']
        elif sys_platform == 'darwin' and ffmpeg_supports_videotoolbox():
            cmd += ['-c:v', 'h264_videotoolbox', '-b:v', '2M']
    cmd.append(str(output_file))
    if verbose:
        subprocess.run(cmd, check=True)
    else:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def copy_video(input_file, output_file):
    """
    直接拷贝视频（无旋转）。

    Args:
        input_file (Path): 输入视频文件路径。
        output_file (Path): 输出视频文件路径。
    """
    cmd = [
        'ffmpeg', '-y', '-i', str(input_file), '-c', 'copy', str(output_file)
    ]
    subprocess.run(cmd, check=True)

def ensure_ffmpeg():
    """
    检查 ffmpeg 是否可用，如不可用则尝试自动安装。
    支持 macOS、Linux、Windows。
    """
    if shutil.which('ffmpeg') and shutil.which('ffprobe'):
        return  # 已安装
    print('未检测到 ffmpeg，正在尝试自动安装...')
    system = platform.system().lower()
    try:
        if system == 'darwin':  # macOS
            # 使用 Homebrew 安装
            if shutil.which('brew'):
                os.system('brew install ffmpeg')
            else:
                print('请先手动安装 Homebrew，然后再运行本程序。')
                sys.exit(1)
        elif system == 'linux':
            # 使用 apt 安装
            if shutil.which('apt'):
                os.system('sudo apt-get update && sudo apt-get install -y ffmpeg')
            else:
                print('请手动安装 ffmpeg（如 yum/dnf/pacman），或参考 https://ffmpeg.org/download.html')
                sys.exit(1)
        elif system == 'windows':
            # Windows 下自动下载并解压 ffmpeg 到本地
            ffmpeg_url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
            tmp_zip = tempfile.mktemp(suffix='.zip')
            print('正在下载 ffmpeg...')
            urllib.request.urlretrieve(ffmpeg_url, tmp_zip)
            with zipfile.ZipFile(tmp_zip, 'r') as zip_ref:
                zip_ref.extractall('.')
            print('请将解压后的 ffmpeg/bin 目录加入系统环境变量，或手动将 ffmpeg.exe 拷贝到本程序目录。')
            print('下载完成后请重新运行本程序。')
            sys.exit(1)
        else:
            print('暂不支持的操作系统，请手动安装 ffmpeg。')
            sys.exit(1)
        # 自动安装后再次检测
        if not (shutil.which('ffmpeg') and shutil.which('ffprobe')):
            print('ffmpeg 自动安装后依然不可用，请手动安装。')
            sys.exit(1)
    except Exception as e:
        print(f'自动安装 ffmpeg 失败，请手动安装。错误信息: {e}')
        sys.exit(1)

def main():
    """
    命令行主入口，参数解析与批量处理逻辑。
    """
    ensure_ffmpeg()  # 检查并自动安装 ffmpeg
    parser = argparse.ArgumentParser(description='批量视频旋转工具')
    parser.add_argument('-f', '--file', type=str, default='.', help='输入视频文件或文件夹路径，默认当前目录')
    parser.add_argument('-o', '--output', type=str, default='.', help='输出文件或文件夹路径，默认当前目录')
    parser.add_argument('-d', '--direction', type=str, choices=['left', 'right', 'auto'], default='auto', help='旋转方向 left/right/auto，默认auto')
    parser.add_argument('--format', type=str, default=None, help='输出视频格式，如 mp4, avi, mkv 等，默认与输入相同')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示 ffmpeg 详细日志')
    parser.add_argument('--gpu', action='store_true', help='如支持则启用 GPU 加速（macOS VideoToolbox，Windows NVIDIA NVENC）')
    args = parser.parse_args()

    input_files = get_video_files(args.file)
    if not input_files:
        print('未找到有效输入视频文件')
        sys.exit(1)

    output_path = Path(args.output)
    # 只判断是否有文件后缀名即可，表示为文件名
    is_output_file = bool(output_path.suffix)
    if is_output_file and len(input_files) > 1:
        print('当 -o 指定为文件名时，只能处理单个输入文件。')
        sys.exit(1)
    # 统一处理循环，进度条始终一行，处理日志单独一行
    for input_file in tqdm(input_files, desc='处理进度', unit='file', leave=True):
        # 决定输出路径和文件名
        if is_output_file:
            out_path = output_path
            ext = args.format if args.format else output_path.suffix[1:]
        else:
            ext = args.format if args.format else input_file.suffix[1:]
            base_name = input_file.stem
            out_name = f'{base_name}_fixed.{ext}'
            out_path = output_path / out_name
            output_path.mkdir(parents=True, exist_ok=True)
        # 旋转逻辑
        if args.direction == 'auto':
            orientation = get_video_orientation(input_file)
            if orientation == 'portrait':
                direction = 'left'
            else:
                tqdm.write(f'正在处理: {input_file.name} -> {out_path.name} [跳过: 横屏]')
                continue
        else:
            direction = args.direction
        tqdm.write(f'正在处理: {input_file.name} -> {out_path.name} [{direction}]')
        rotate_video_ffmpeg(input_file, out_path, direction, verbose=args.verbose, use_gpu=args.gpu)
    print('全部处理完成！')

if __name__ == '__main__':
    # 程序入口
    main()
