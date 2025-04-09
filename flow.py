from pocketflow import Flow
from nodes import (
    InputNode, 
    SubtitleExtractNode, 
    SubtitleProcessNode,
    SummaryGenerationNode,
    HTMLGenerationNode,
    ErrorHandlingNode
)

def create_bilibili_summary_flow():
    """创建B站视频总结流程"""
    # 创建节点
    input_node = InputNode()
    subtitle_extract_node = SubtitleExtractNode()
    subtitle_process_node = SubtitleProcessNode()
    summary_generation_node = SummaryGenerationNode()
    html_generation_node = HTMLGenerationNode()
    error_handling_node = ErrorHandlingNode()
    
    # 连接节点 - 使用普通路径连接
    input_node >> subtitle_extract_node
    subtitle_extract_node >> subtitle_process_node
    subtitle_process_node >> summary_generation_node
    summary_generation_node >> html_generation_node
    
    # 注意：在pocketflow 0.0.1版本中可能没有add_edge方法
    # 我们需要在节点的post方法中处理错误路径
    
    # 创建流程，从输入节点开始
    return Flow(start=input_node)

# 导出流程
bilibili_summary_flow = create_bilibili_summary_flow()