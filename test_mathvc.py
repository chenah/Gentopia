#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MATHVC系统测试脚本
用于验证系统各组件是否正常工作
"""

import os
import sys
import time
from mathvc_system import MATHVCSystem


def test_qwen_client():
    """测试Qwen客户端是否正常工作"""
    print("=" * 50)
    print("测试1: Qwen客户端")
    print("=" * 50)
    
    try:
        from gentopia.llm.client.qwen import QwenClient
        
        # 创建Qwen客户端实例
        client = QwenClient(
            model_name="Qwen/Qwen3-Next-80B-A3B-Instruct",
            base_url="https://api-inference.modelscope.cn/v1",
            api_key="ms-38f326cf-a318-43c3-bdfc-6b3395773378",
            params={"temperature": 0.7}
        )
        
        # 测试简单对话
        response = client.chat_completion([{"role": "user", "content": "你好，请简单介绍一下自己"}])
        
        if response and response.state == "success":
            print("✓ Qwen客户端测试成功")
            print(f"响应: {response.output[:100]}...")
        else:
            print("✗ Qwen客户端测试失败")
            return False
    except Exception as e:
        print(f"✗ Qwen客户端测试失败: {str(e)}")
        return False
    
    return True


def test_agent_configs():
    """测试代理配置文件是否正确加载"""
    print("\n" + "=" * 50)
    print("测试2: 代理配置文件")
    print("=" * 50)
    
    config_dir = "f:\\Gentopia\\configs"
    expected_configs = [
        "mathvc_metaplanner.yaml",
        "mathvc_student.yaml",
        "mathvc_teacher.yaml",
        "mathvc_expert.yaml",
        "mathvc_evaluator.yaml"
    ]
    
    for config_file in expected_configs:
        config_path = os.path.join(config_dir, config_file)
        if os.path.exists(config_path):
            print(f"✓ 配置文件存在: {config_file}")
        else:
            print(f"✗ 配置文件不存在: {config_file}")
            return False
    
    return True


def test_agent_initialization():
    """测试代理初始化是否成功"""
    print("\n" + "=" * 50)
    print("测试3: 代理初始化")
    print("=" * 50)
    
    try:
        # 初始化MATHVC系统
        mathvc = MATHVCSystem()
        
        # 检查所有代理是否成功初始化
        expected_agents = [
            "mathvc_metaplanner",
            "mathvc_student",
            "mathvc_teacher",
            "mathvc_expert",
            "mathvc_evaluator"
        ]
        
        for agent_name in expected_agents:
            if agent_name in mathvc.agents:
                print(f"✓ 代理初始化成功: {agent_name}")
            else:
                print(f"✗ 代理初始化失败: {agent_name}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ 代理初始化测试失败: {str(e)}")
        return False


def test_system_processing():
    """测试系统处理任务的能力"""
    print("\n" + "=" * 50)
    print("测试4: 系统任务处理")
    print("=" * 50)
    
    try:
        # 初始化MATHVC系统
        mathvc = MATHVCSystem()
        
        # 测试简单任务
        task = "请解释一下什么是勾股定理"
        print(f"测试任务: {task}")
        print("处理中...")
        
        start_time = time.time()
        response = mathvc.process_task(task)
        end_time = time.time()
        
        if response:
            print(f"✓ 系统任务处理成功")
            print(f"处理时间: {end_time - start_time:.2f}秒")
            print(f"响应长度: {len(response)}字符")
            print(f"响应预览: {response[:200]}...")
        else:
            print("✗ 系统任务处理失败: 响应为空")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 系统任务处理测试失败: {str(e)}")
        return False


def test_conversation_history():
    """测试对话历史功能"""
    print("\n" + "=" * 50)
    print("测试5: 对话历史")
    print("=" * 50)
    
    try:
        # 初始化MATHVC系统
        mathvc = MATHVCSystem()
        
        # 处理一个任务
        mathvc.process_task("什么是二次函数？")
        
        # 获取对话历史
        history = mathvc.get_conversation_history()
        
        if len(history) >= 2:  # 至少包含用户输入和系统响应
            print(f"✓ 对话历史功能正常")
            print(f"历史记录数: {len(history)}")
            print(f"用户输入: {history[0]['content']}")
            print(f"系统响应预览: {history[1]['content'][:100]}...")
        else:
            print(f"✗ 对话历史功能异常: 历史记录数不足 {len(history)}")
            return False
        
        # 测试清空对话历史
        mathvc.clear_conversation_history()
        history = mathvc.get_conversation_history()
        
        if len(history) == 0:
            print("✓ 清空对话历史功能正常")
        else:
            print(f"✗ 清空对话历史功能异常: 清空后仍有 {len(history)} 条记录")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 对话历史测试失败: {str(e)}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("开始运行MATHVC系统测试...")
    print()
    
    tests = [
        test_qwen_client,
        test_agent_configs,
        test_agent_initialization,
        test_system_processing,
        test_conversation_history
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    print("=" * 50)
    
    if passed == total:
        print("🎉 所有测试通过！MATHVC系统已准备就绪。")
        return True
    else:
        print("⚠️ 部分测试失败，请检查系统配置。")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)