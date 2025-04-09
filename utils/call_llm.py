import os
import json
import openai

def call_llm(prompt, model_name=None, base_url=None, api_key=None):
    """
    调用大语言模型进行文本生成
    
    Args:
        prompt: 输入提示文本
        model_name: 模型名称，如果为None则使用默认模型
        base_url: API基础URL，如果为None则使用默认URL
        api_key: OpenAI API密钥，如果为None则从环境变量获取
    
    Returns:
        返回模型生成的回复内容
    """
    try:
        # 设置OpenAI客户端参数
        client_kwargs = {}
        
        # 设置API密钥
        if api_key:
            client_kwargs["api_key"] = api_key
        else:
            api_key_env = os.environ.get("OPENAI_API_KEY")
            if not api_key_env:
                raise ValueError("未设置OPENAI_API_KEY环境变量或未提供api_key参数")
            client_kwargs["api_key"] = api_key_env
        
        # 设置base_url（如果提供）
        if base_url:
            client_kwargs["base_url"] = base_url
            
        # 创建客户端
        client = openai.OpenAI(**client_kwargs)
        
        # 设置模型名称（如果未提供则使用默认值）
        model = model_name or "gpt-3.5-turbo"
        
        # 发送请求
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"调用LLM失败: {str(e)}")

def generate_summary(subtitle_text, video_url, model_name=None, base_url=None, api_key=None):
    """
    根据字幕内容生成视频摘要
    
    Args:
        subtitle_text: 字幕文本内容
        video_url: 视频URL
        model_name: 模型名称，如果为None则使用默认模型
        base_url: API基础URL，如果为None则使用默认URL
        api_key: OpenAI API密钥，如果为None则从环境变量获取
    
    Returns:
        返回生成的摘要数据
    """
    # 构建提示文本
    prompt = f"""
我需要你为一个视频生成一个全面的中文摘要。我会给你字幕文本。

视频URL: {video_url}

字幕内容:
{subtitle_text[:15000] if len(subtitle_text) > 15000 else subtitle_text}

请提供以下格式的摘要（用JSON格式输出）:
{{
  "标题": "一个简短但信息丰富的标题",
  "核心内容": "视频的核心要点（一句话）",
  "关键点": ["关键点1", "关键点2", "关键点3", ...],
  "详细摘要": "一个由多个段落组成的详细摘要，捕捉视频的主要内容，不超过800字",
  "结论": "视频总结或结论"
}}

请确保你的回答是完全有效的JSON格式。不要添加任何前后缀，如```json或类似标记。
"""
    
    # 调用LLM
    try:
        response = call_llm(prompt, model_name, base_url, api_key)
        
        # 解析回复为JSON
        try:
            summary_data = json.loads(response)
            # 验证JSON数据包含所有需要的字段
            required_fields = ["标题", "核心内容", "关键点", "详细摘要", "结论"]
            for field in required_fields:
                if field not in summary_data:
                    raise ValueError(f"返回的摘要数据缺少必要字段: {field}")
            
            return summary_data
        except json.JSONDecodeError:
            # 如果解析失败，尝试提取JSON部分
            import re
            json_pattern = r'({[\s\S]*})'
            match = re.search(json_pattern, response)
            if match:
                try:
                    summary_data = json.loads(match.group(1))
                    return summary_data
                except:
                    pass
            
            # 如果仍然无法解析，则抛出错误
            raise ValueError("LLM返回的内容不是有效的JSON格式")
    except Exception as e:
        raise Exception(f"生成摘要失败: {str(e)}")

if __name__ == "__main__":
    # 测试函数
    prompt = "人工智能的未来是什么？"
    print(call_llm(prompt))
    
    # 测试摘要生成
    test_subtitle = """
    0:00 大家好，欢迎来到这个视频。
    0:05 今天我们将讨论人工智能的发展。
    0:10 人工智能正在改变我们的生活方式。
    0:15 从简单的语音助手到复杂的自动驾驶系统。
    0:20 这些技术都依赖于机器学习算法。
    """
    result = generate_summary(test_subtitle, "https://www.bilibili.com/video/BV123456789")
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
