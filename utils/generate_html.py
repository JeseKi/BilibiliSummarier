import os
import json
from datetime import datetime

def generate_html(summary, video_url, subtitle_data=None, output_path=None):
    """
    生成包含视频摘要的HTML页面
    
    参数:
        summary (dict): 摘要信息字典
        video_url (str): 视频URL
        subtitle_data (dict, optional): 字幕数据
        output_path (str, optional): 输出文件路径
        
    返回:
        str: 生成的HTML文件路径
    """
    # 获取视频ID
    if "bilibili.com/video/" in video_url:
        video_id = video_url.split("bilibili.com/video/")[1].split("?")[0].split("/")[0]
    else:
        video_id = "unknown"
    
    # 处理关键点
    key_points_html = ""
    if summary.get("关键点"):
        for i, point in enumerate(summary["关键点"]):
            key_points_html += f'<li><span class="point-number">{i+1}</span><span class="point-content">{point}</span></li>\n'
    
    # 当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 生成HTML内容
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{summary.get("标题", "视频摘要")} - 哔哩哔哩视频总结器</title>
    <style>
        :root {{
            --primary-color: #FB7299;
            --secondary-color: #23ADE5;
            --background-color: #f6f7f8;
            --card-background: #ffffff;
            --text-color: #18191c;
            --text-secondary: #61666d;
            --border-radius: 12px;
            --shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 30px;
            padding-top: 20px;
        }}
        
        .logo {{
            font-size: 24px;
            font-weight: bold;
            color: var(--primary-color);
            margin-bottom: 10px;
        }}
        
        h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            line-height: 1.4;
        }}
        
        .video-info {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            font-size: 14px;
            margin-bottom: 10px;
        }}
        
        .video-info a {{
            color: var(--secondary-color);
            text-decoration: none;
            margin-left: 5px;
        }}
        
        .card {{
            background-color: var(--card-background);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            padding: 24px;
            margin-bottom: 24px;
        }}
        
        .card-title {{
            font-size: 18px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
        }}
        
        .card-title::before {{
            content: "";
            display: inline-block;
            width: 4px;
            height: 18px;
            background-color: var(--primary-color);
            margin-right: 10px;
            border-radius: 2px;
        }}
        
        .core-content {{
            font-size: 16px;
            line-height: 1.8;
        }}
        
        .key-points-list {{
            list-style: none;
            margin-top: 12px;
        }}
        
        .key-points-list li {{
            margin-bottom: 12px;
            display: flex;
            align-items: flex-start;
        }}
        
        .point-number {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 24px;
            height: 24px;
            background-color: var(--primary-color);
            color: white;
            border-radius: 50%;
            font-size: 14px;
            margin-right: 10px;
            flex-shrink: 0;
        }}
        
        .point-content {{
            flex: 1;
        }}
        
        .summary-text {{
            line-height: 1.8;
            text-align: justify;
        }}
        
        .conclusion {{
            font-size: 16px;
            line-height: 1.8;
            padding: 16px;
            background-color: rgba(251, 114, 153, 0.05);
            border-left: 4px solid var(--primary-color);
            border-radius: 0 var(--border-radius) var(--border-radius) 0;
        }}
        
        footer {{
            text-align: center;
            margin-top: 50px;
            color: var(--text-secondary);
            font-size: 14px;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 16px;
            }}
            
            h1 {{
                font-size: 22px;
            }}
            
            .card {{
                padding: 16px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">哔哩哔哩视频总结器</div>
            <h1>{summary.get("标题", "视频摘要")}</h1>
            <div class="video-info">
                视频链接：<a href="{video_url}" target="_blank">BV{video_id}</a>
            </div>
        </header>
        
        <main>
            <section class="card">
                <h2 class="card-title">核心内容</h2>
                <div class="core-content">
                    {summary.get("核心内容", "暂无内容")}
                </div>
            </section>
            
            <section class="card">
                <h2 class="card-title">关键点</h2>
                <ul class="key-points-list">
                    {key_points_html}
                </ul>
            </section>
            
            <section class="card">
                <h2 class="card-title">详细摘要</h2>
                <div class="summary-text">
                    {summary.get("详细摘要", "暂无内容")}
                </div>
            </section>
            
            <section class="card">
                <h2 class="card-title">结论</h2>
                <div class="conclusion">
                    {summary.get("结论", "暂无内容")}
                </div>
            </section>
        </main>
        
        <footer>
            由哔哩哔哩视频总结器生成 - {current_time}
        </footer>
    </div>
</body>
</html>
"""
    
    # 确定输出路径
    if not output_path:
        if video_id != "unknown":
            filename = f"bilibili_summary_{video_id}.html"
        else:
            filename = f"bilibili_summary_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
        
        output_path = os.path.join(os.getcwd(), filename)
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path

if __name__ == "__main__":
    # 测试函数
    summary = {
        "标题": "人工智能：改变世界的力量",
        "核心内容": "本视频讨论了人工智能技术的快速发展及其对社会的影响。人工智能已经渗透到我们日常生活的方方面面，从语音助手到自动驾驶系统。它正在改变工作方式、医疗健康和教育等领域。",
        "关键点": [
            "人工智能技术正在快速发展",
            "AI已应用于语音助手和自动驾驶等领域",
            "机器学习是AI发展的核心技术",
            "AI将改变未来的工作方式",
            "人们需要关注AI发展带来的伦理问题"
        ],
        "详细摘要": "人工智能技术在近年来取得了突飞猛进的发展，已经开始深刻地改变我们的生活方式和工作方式。从我们日常使用的语音助手，到复杂的自动驾驶系统，人工智能正在各个领域展示其强大的能力。机器学习算法的进步使计算机能够从大量数据中学习并做出决策，这是人工智能发展的核心。在医疗领域，AI可以辅助诊断疾病；在教育方面，AI可以提供个性化学习体验；在工业生产中，AI可以优化流程并提高效率。然而，随着AI技术的广泛应用，我们也需要关注数据隐私、算法偏见等伦理问题。",
        "结论": "人工智能将继续以惊人的速度发展，并深刻改变我们的社会。我们需要积极拥抱这一技术革命，同时谨慎应对其带来的挑战，确保AI的发展造福全人类。"
    }
    
    output_path = generate_html(summary, "https://www.bilibili.com/video/BV123456789")
    print(f"HTML文件已生成: {output_path}")
