import os
import subprocess
import tempfile
import json
from pathlib import Path

def download_subtitle(video_url, sessdata=None, output_dir=None):
    """
    使用yutto下载B站视频的字幕
    
    参数:
        video_url (str): B站视频的URL
        sessdata (str, optional): B站的SESSDATA cookie
        output_dir (str, optional): 输出目录，默认为临时目录
        
    返回:
        dict: 包含字幕文件路径和视频信息的字典
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="bilibili_summarizer_")
    else:
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
    
    # 构建yutto命令
    cmd = ["yutto", video_url, "--subtitle-only", "--dir", output_dir]
    
    # 如果提供了SESSDATA，添加到命令中
    if sessdata:
        cmd.extend(["--sessdata", sessdata])
    
    # 运行yutto命令
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("yutto命令执行成功")
        
        # 查找下载的字幕文件
        subtitle_files = list(Path(output_dir).glob("**/*.srt"))
        if not subtitle_files:
            subtitle_files = list(Path(output_dir).glob("**/*.ass"))
        
        if not subtitle_files:
            raise Exception("未找到下载的字幕文件")
        
        # 获取视频信息
        video_id = video_url.split("/")[-1].split("?")[0]
        if video_id.startswith("av"):
            video_id = video_id[2:]
        elif video_id.startswith("BV"):
            # BV号，这里简化处理
            pass
        
        # 返回结果
        return {
            "subtitle_files": [str(f) for f in subtitle_files],
            "video_url": video_url,
            "video_id": video_id,
            "output_dir": output_dir
        }
        
    except subprocess.CalledProcessError as e:
        print(f"yutto命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        raise Exception(f"字幕下载失败: {e}")

if __name__ == "__main__":
    # 测试函数
    url = "https://www.bilibili.com/video/BV1GJ411x7h7"
    result = download_subtitle(url)
    print(f"下载结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
