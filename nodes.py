from pocketflow import Node
from utils.call_llm import call_llm, generate_summary
from utils.download_subtitle import download_subtitle
from utils.process_subtitle import process_subtitle_file
from utils.generate_html import generate_html
import os
import json

class InputNode(Node):
    """接收用户输入的节点"""
    def exec(self, _):
        # 获取视频URL和必选的SESSDATA
        video_url = input("请输入B站视频URL: ")
        sessdata = input("请输入B站SESSDATA (必选): ")
        
        # 验证SESSDATA是否提供
        while not sessdata.strip():
            print("⚠️ SESSDATA是必选的，否则无法下载字幕！")
            sessdata = input("请输入B站SESSDATA (必选): ")
        
        # 获取OpenAI相关配置
        print("\n配置大语言模型 (如果使用默认值，请直接按回车)")
        api_key = input("请输入OpenAI API密钥 (可选，默认使用环境变量OPENAI_API_KEY): ")
        model_name = input("请输入模型名称 (可选，默认使用gpt-3.5-turbo): ")
        base_url = input("请输入API基础URL (可选，默认使用OpenAI官方API): ")
        
        return {
            "video_url": video_url,
            "sessdata": sessdata,
            "api_key": api_key.strip() if api_key.strip() else None,
            "model_name": model_name.strip() if model_name.strip() else None,
            "base_url": base_url.strip() if base_url.strip() else None
        }
    
    def post(self, shared, prep_res, exec_res):
        # 将用户输入存储到共享数据中
        shared["video_url"] = exec_res["video_url"]
        shared["sessdata"] = exec_res["sessdata"]
        shared["api_key"] = exec_res["api_key"]
        shared["model_name"] = exec_res["model_name"]
        shared["base_url"] = exec_res["base_url"]
        return "default"

class SubtitleExtractNode(Node):
    """使用yutto下载字幕的节点"""
    def prep(self, shared):
        return {
            "video_url": shared["video_url"],
            "sessdata": shared["sessdata"]
        }
    
    def exec(self, input_data):
        print("正在下载字幕，请稍候...")
        
        try:
            subtitle_info = download_subtitle(
                input_data["video_url"],
                input_data["sessdata"]
            )
            print(f"字幕下载成功，共找到 {len(subtitle_info['subtitle_files'])} 个字幕文件")
            return subtitle_info
        except Exception as e:
            print(f"字幕下载失败: {str(e)}")
            # 返回错误信息，后续节点会处理
            return {"error": str(e)}
    
    def post(self, shared, prep_res, exec_res):
        if "error" in exec_res:
            shared["error"] = exec_res["error"]
            # 因为没有错误处理路径，我们在这里直接处理错误
            print(f"\n⚠️ 处理过程中出现错误: {exec_res['error']}")
            print("请检查错误信息并重试。")
            
            # 可能的错误原因和解决建议
            if "SESSDATA" in str(exec_res["error"]):
                print("\n可能是SESSDATA无效或已过期。请确保使用有效的SESSDATA。")
                print("获取SESSDATA的方法: 登录B站 -> F12打开控制台 -> Application标签 -> Cookies -> SESSDATA")
            elif "yutto" in str(exec_res["error"]).lower():
                print("\n请确保已正确安装yutto:")
                print("pip install yutto")
            
            return None  # 停止流程
        
        # 存储字幕信息到共享数据
        shared["subtitle_info"] = exec_res
        return "default"

class SubtitleProcessNode(Node):
    """处理字幕内容的节点"""
    def prep(self, shared):
        return shared["subtitle_info"]
    
    def exec(self, subtitle_info):
        print("正在处理字幕内容...")
        
        try:
            # 取第一个字幕文件进行处理
            subtitle_file = subtitle_info["subtitle_files"][0]
            subtitle_data = process_subtitle_file(subtitle_file)
            return subtitle_data
        except Exception as e:
            print(f"字幕处理失败: {str(e)}")
            return {"error": str(e)}
    
    def post(self, shared, prep_res, exec_res):
        if "error" in exec_res:
            shared["error"] = exec_res["error"]
            print(f"\n⚠️ 处理过程中出现错误: {exec_res['error']}")
            return None  # 停止流程
        
        # 存储处理后的字幕数据
        shared["subtitle_data"] = exec_res
        return "default"

class SummaryGenerationNode(Node):
    """生成摘要的节点"""
    def prep(self, shared):
        return {
            "subtitle_data": shared["subtitle_data"],
            "video_url": shared["video_url"],
            "model_name": shared["model_name"],
            "base_url": shared["base_url"],
            "api_key": shared["api_key"]
        }
    
    def exec(self, input_data):
        print("正在生成视频摘要，这可能需要一些时间...")
        
        try:
            summary = generate_summary(
                input_data["subtitle_data"]["full_text"],
                input_data["video_url"],
                input_data["model_name"],
                input_data["base_url"],
                input_data["api_key"]
            )
            return summary
        except Exception as e:
            print(f"摘要生成失败: {str(e)}")
            return {"error": str(e)}
    
    def post(self, shared, prep_res, exec_res):
        if "error" in exec_res:
            shared["error"] = exec_res["error"]
            print(f"\n⚠️ 处理过程中出现错误: {exec_res['error']}")
            return None  # 停止流程
        
        # 存储摘要结果
        shared["summary"] = exec_res
        
        # 打印摘要预览
        print("\n===== 摘要预览 =====")
        print(f"标题: {exec_res['标题']}")
        print(f"核心内容: {exec_res['核心内容']}")
        print("关键点:")
        for i, point in enumerate(exec_res['关键点']):
            print(f"  {i+1}. {point}")
        print(f"详细摘要: {exec_res['详细摘要'][:100]}...")
        print(f"结论: {exec_res['结论']}")
        print("====================\n")
        
        return "default"

class HTMLGenerationNode(Node):
    """生成HTML页面的节点"""
    def prep(self, shared):
        return {
            "summary": shared["summary"],
            "video_url": shared["video_url"],
            "subtitle_data": shared.get("subtitle_data")
        }
    
    def exec(self, input_data):
        print("正在生成HTML页面...")
        
        try:
            html_path = generate_html(
                input_data["summary"],
                input_data["video_url"],
                input_data.get("subtitle_data")
            )
            return html_path
        except Exception as e:
            print(f"HTML生成失败: {str(e)}")
            return {"error": str(e)}
    
    def post(self, shared, prep_res, exec_res):
        if "error" in exec_res:
            shared["error"] = exec_res["error"]
            print(f"\n⚠️ 处理过程中出现错误: {exec_res['error']}")
            return None  # 停止流程
        
        # 存储HTML路径
        shared["html_path"] = exec_res
        print(f"\n✅ 摘要已生成! HTML文件路径: {exec_res}")
        return "default"

class ErrorHandlingNode(Node):
    """错误处理节点"""
    def prep(self, shared):
        return shared.get("error", "未知错误")
    
    def exec(self, error):
        print(f"⚠️ 处理过程中出现错误: {error}")
        print("请检查错误信息并重试。")
        
        # 可能的错误原因和解决建议
        if "SESSDATA" in str(error):
            print("\n可能是SESSDATA无效或已过期。请确保使用有效的SESSDATA。")
            print("获取SESSDATA的方法: 登录B站 -> F12打开控制台 -> Application标签 -> Cookies -> SESSDATA")
        elif "yutto" in str(error).lower():
            print("\n请确保已正确安装yutto:")
            print("pip install yutto")
        
        return error
    
    def post(self, shared, prep_res, exec_res):
        return "default"