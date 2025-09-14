import os
import json
from flask import Flask, render_template, request, jsonify
from mathvc_system_meta_planner import MATHVCMetaPlannerSystem

app = Flask(__name__, template_folder='templates')

# 初始化MATHVC系统
mathvc_system = MATHVCMetaPlannerSystem()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天消息的API端点"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': '消息不能为空'}), 400
        
        # 调用MATHVC系统的Meta Planner处理流程
        result = mathvc_system.meta_planner_process(user_message)
        
        # 根据结果类型返回不同格式的响应
        if result['type'] == 'single_character_response':
            response_data = {
                'response': result['response'],
                'next_speaker': result['speaker'].replace("mathvc_", "").capitalize(),
                'current_stage': result['current_stage'],
                'meta_planner_status': result['meta_planner_status']
            }
        elif result['type'] == 'wait_for_user':
            response_data = {
                'response': result['message'],
                'next_speaker': '用户',
                'current_stage': result['current_stage'],
                'meta_planner_status': result['meta_planner_status']
            }
        elif result['type'] == 'mixed_wait':
            response_data = {
                'response': result['message'],
                'next_speaker': result.get('next_speaker', '系统').replace("mathvc_", "").capitalize(),
                'current_stage': result['current_stage'],
                'meta_planner_status': result['meta_planner_status']
            }
        else:
            response_data = {
                'response': '系统处理中...',
                'next_speaker': '系统',
                'current_stage': result.get('current_stage', '未知阶段')
            }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': f'处理消息时出错: {str(e)}'}), 500

@app.route('/api/history')
def history():
    """获取对话历史"""
    try:
        conversation_history = mathvc_system.get_conversation_history()
        return jsonify({'history': conversation_history})
    except Exception as e:
        return jsonify({'error': f'获取历史记录时出错: {str(e)}'}), 500

@app.route('/api/status')
def status():
    """获取系统状态"""
    try:
        current_stage = mathvc_system.get_current_stage_name()
        # 简化实现，实际可以根据系统状态动态确定
        next_speaker = "待定"
        is_user_turn = True
        
        return jsonify({
            'current_stage': current_stage,
            'next_speaker': next_speaker,
            'is_user_turn': is_user_turn
        })
    except Exception as e:
        return jsonify({'error': f'获取状态时出错: {str(e)}'}), 500

@app.route('/api/clear', methods=['POST'])
def clear():
    """清空对话历史"""
    try:
        # 重新初始化系统以清空状态
        global mathvc_system
        mathvc_system = MATHVCMetaPlannerSystem()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': f'清空对话时出错: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)