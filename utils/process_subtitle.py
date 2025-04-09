import re
import os
import json
from pathlib import Path

def parse_srt(srt_file):
    """
    解析SRT字幕文件
    
    参数:
        srt_file (str): SRT文件路径
        
    返回:
        list: 包含字幕内容和时间戳的列表
    """
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分割字幕块
    subtitle_blocks = re.split(r'\n\s*\n', content.strip())
    subtitles = []
    
    for block in subtitle_blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        
        # 第一行是序号
        index = lines[0]
        
        # 第二行是时间戳
        time_line = lines[1]
        time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', time_line)
        if not time_match:
            continue
            
        start_time, end_time = time_match.groups()
        
        # 剩余行是字幕文本
        text = ' '.join(lines[2:])
        
        subtitles.append({
            'index': index,
            'start_time': start_time,
            'end_time': end_time,
            'text': text
        })
    
    return subtitles

def combine_subtitles(subtitles, max_gap_seconds=2):
    """
    合并相近的字幕行，形成更连贯的段落
    
    参数:
        subtitles (list): 字幕列表
        max_gap_seconds (int): 合并的最大时间间隔（秒）
        
    返回:
        list: 合并后的字幕列表
    """
    if not subtitles:
        return []
    
    def time_to_seconds(time_str):
        """将时间字符串转换为秒数"""
        h, m, s = time_str.replace(',', '.').split(':')
        return int(h) * 3600 + int(m) * 60 + float(s)
    
    combined = []
    current_group = {
        'start_time': subtitles[0]['start_time'],
        'end_time': subtitles[0]['end_time'],
        'text': subtitles[0]['text']
    }
    
    for i in range(1, len(subtitles)):
        current_end = time_to_seconds(current_group['end_time'])
        next_start = time_to_seconds(subtitles[i]['start_time'])
        
        # 如果时间间隔小于阈值，则合并
        if next_start - current_end <= max_gap_seconds:
            current_group['end_time'] = subtitles[i]['end_time']
            current_group['text'] += ' ' + subtitles[i]['text']
        else:
            combined.append(current_group)
            current_group = {
                'start_time': subtitles[i]['start_time'],
                'end_time': subtitles[i]['end_time'],
                'text': subtitles[i]['text']
            }
    
    combined.append(current_group)
    return combined

def process_subtitle_file(subtitle_file):
    """
    处理字幕文件，解析并合并字幕
    
    参数:
        subtitle_file (str): 字幕文件路径
        
    返回:
        dict: 处理后的字幕信息
    """
    file_ext = os.path.splitext(subtitle_file)[1].lower()
    
    if file_ext == '.srt':
        # 解析SRT文件
        subtitles = parse_srt(subtitle_file)
        
        # 合并相近的字幕
        combined_subtitles = combine_subtitles(subtitles)
        
        # 提取纯文本用于摘要
        full_text = ' '.join([s['text'] for s in combined_subtitles])
        
        return {
            'subtitle_file': subtitle_file,
            'subtitles': combined_subtitles,
            'full_text': full_text
        }
    else:
        # 目前只支持SRT格式
        raise ValueError(f"暂不支持的字幕格式: {file_ext}")

if __name__ == "__main__":
    # 测试函数
    import sys
    if len(sys.argv) > 1:
        subtitle_file = sys.argv[1]
    else:
        # 默认测试文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        subtitle_file = os.path.join(script_dir, "..", "test_subtitle.srt")
    
    if os.path.exists(subtitle_file):
        result = process_subtitle_file(subtitle_file)
        print(f"处理结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print(f"字幕文件不存在: {subtitle_file}")
