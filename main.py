from flow import bilibili_summary_flow

def main():
    """启动B站视频总结器"""
    print("="*50)
    print("欢迎使用哔哩哔哩视频总结器!")
    print("本工具使用yutto获取B站视频字幕，然后生成视频内容摘要")
    print("="*50)
    
    # 初始化共享数据
    shared = {}
    
    # 运行流程
    bilibili_summary_flow.run(shared)
    
    # 如果成功生成了HTML文件，提示用户
    if "html_path" in shared:
        print(f"\n您可以打开以下文件查看完整摘要:")
        print(f"file://{shared['html_path']}")
        print("\n感谢使用哔哩哔哩视频总结器!")

if __name__ == "__main__":
    main()