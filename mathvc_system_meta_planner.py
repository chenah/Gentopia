import json
import os
import random
import time
import requests
from typing import List, Dict, Any, Optional

class MATHVCMetaPlannerSystem:
    """
    MATHVC Meta Planner系统 - 严格按照论文设计的中央控制器
    
    基于论文《MATHVC: An LLM-Simulated Multi-Character Virtual Classroom for Mathematics Education》
    实现Meta Planner中央控制，包含三个核心组件：
    1. Task Schema Generator - 生成任务结构
    2. Dialogue Speaker Control - 控制发言者
    3. Collaboration Stage Monitor - 监控协作阶段
    """
    
    # 协作问题解决的五个阶段（基于论文）
    COLLABORATION_STAGES = [
        "problem_understanding",  # 问题理解
        "modeling",              # 建模
        "calculation",           # 计算
        "validation",            # 验证
        "summary"                # 总结
    ]
    
    STAGE_NAMES = {
        "problem_understanding": "问题理解阶段",
        "modeling": "建模阶段", 
        "calculation": "计算阶段",
        "validation": "验证阶段",
        "summary": "总结阶段"
    }
    
    def __init__(self, config_dir: str = "f:\\Gentopia\\configs"):
        """初始化MATHVC Meta Planner系统"""
        self.config_dir = config_dir
        self.conversation_history = []
        self.current_task = None
        self.current_stage_index = 0
        
        # Meta Planner核心组件
        self.task_schema = None
        self.character_schemas = {}
        
        # 角色定义
        self.agents = {
            "mathvc_alice": {
                "name": "Alice", 
                "math_level": "较差", 
                "personality": "谨慎但容易犯错",
                "description": "数学能力较差，容易犯基础错误，但态度谨慎"
            },
            "mathvc_bob": {
                "name": "Bob", 
                "math_level": "中等", 
                "personality": "积极参与但偶尔遗漏",
                "description": "数学能力中等，积极参与讨论，偶尔会遗漏细节"
            },
            "mathvc_charlie": {
                "name": "Charlie", 
                "math_level": "较好", 
                "personality": "自信但可能过度复杂化",
                "description": "数学能力较好，很少犯错，但可能会过度复杂化问题"
            }
        }
        
        # API配置 - 使用正确的ModelScope API
        self.api_base_url = "https://api-inference.modelscope.cn/v1"
        self.api_key = "ms-38f326cf-a318-43c3-bdfc-6b3395773378"
        self.model_name = "Qwen/Qwen3-Next-80B-A3B-Instruct"
        
        print("MATHVC Meta Planner系统初始化完成")
    
    def meta_planner_process(self, user_input: str) -> dict:
        """
        Meta Planner主处理流程 - 中央控制器
        严格按照论文架构实现（第327-338行动态等待机制）
        """
        print(f"Meta Planner处理用户输入: {user_input}")
        
        # 保存用户输入到对话历史
        self.conversation_history.append({
            'speaker': '用户',
            'message': user_input,
            'timestamp': time.time()
        })
        
        # If this is the first input, generate the task and character schemas
        if len(self.conversation_history) == 1:
            self._generate_task_schema(user_input)
            self._generate_character_schemas()
            return self._generate_initial_discussion(user_input)
        
        # 后续输入：Meta Planner的Dialogue Speaker Control
        speaker_control_result = self._dialogue_speaker_control(user_input)
        
        # 监控协作阶段推进
        self._monitor_collaboration_stage()
        
        return speaker_control_result

    def _generate_initial_discussion(self, user_input: str) -> Dict[str, Any]:
        """
        生成初始的多角色讨论
        """
        initial_discussion = []
        for agent_name in self.agents:
            response = self._generate_character_response(agent_name, user_input)
            initial_discussion.append({
                'speaker': self.agents[agent_name]['name'],
                'message': response
            })
            self.conversation_history.append({
                'speaker': self.agents[agent_name]['name'],
                'message': response,
                'timestamp': time.time()
            })
        return {'initial_discussion': initial_discussion}

    def _generate_task_schema(self, user_input: str):
        """
        Generates the Task Schema based on the user's problem description.
        This is the ground-truth model for solving the problem.
        """
        prompt = f"""
        Based on the following math problem, create a Task Schema in JSON format.
        The schema should decompose the problem into sub-tasks, and for each sub-task, identify the necessary variables and their correct values.

        Problem: {user_input}

        Please only output the JSON object.
        """
        
        try:
            response_text = self._call_llm(prompt, max_tokens=1500)
            # Clean the response to ensure it's valid JSON
            clean_response = response_text.strip().replace('`', '')
            if clean_response.startswith('json'):
                clean_response = clean_response[4:]
            self.task_schema = json.loads(clean_response)
            print("Task Schema generated successfully.")
        except Exception as e:
            print(f"Error generating or parsing Task Schema: {e}")
            self.task_schema = None # Ensure schema is None if generation fails

    def _generate_character_schemas(self):
        """
        Generates Character Schemas for each agent by injecting potential errors
        into the Task Schema based on their characteristics.
        """
        if not self.task_schema:
            print("Cannot generate Character Schemas without a Task Schema.")
            return

        for agent_name, agent_info in self.agents.items():
            task_schema_str = json.dumps(self.task_schema, indent=4)
            math_level = agent_info['math_level']
            personality = agent_info['personality']

            prompt = f"""
            You are simulating a middle school student with the following characteristics:
            - Math Skill Level: {math_level}
            - Personality: {personality}

            Here is the correct Task Schema for a math problem:
            {task_schema_str}

            Based on the student's characteristics, please modify this JSON schema to reflect a common mistake they might make. 
            - If the skill level is '较好' (good), make a very subtle mistake or no mistake at all.
            - If the skill level is '中等' (medium), make a plausible calculation or modeling error.
            - If the skill level is '较差' (poor), make a more fundamental misunderstanding or calculation error.

            Only output the modified JSON object, with no other text or explanations.
            """

            try:
                modified_schema_str = self._call_llm(prompt, max_tokens=1500)
                # Clean the response to ensure it's valid JSON
                clean_response = modified_schema_str.strip().replace('`', '')
                if clean_response.startswith('json'):
                    clean_response = clean_response[4:]
                self.character_schemas[agent_name] = json.loads(clean_response)
                print(f"Generated and modified character schema for {agent_name} ({math_level} level).")
            except Exception as e:
                print(f"Error generating character schema for {agent_name}: {e}. Using a direct copy instead.")
                self.character_schemas[agent_name] = json.loads(json.dumps(self.task_schema))
    
    def _dialogue_speaker_control(self, user_input: str) -> Dict[str, Any]:
        """
        Dialogue Speaker Control模块 - 严格按照论文第327-338行实现
        动态控制对话流程和等待机制：
        1. 仅用户候选: 无限等待用户输入
        2. 仅代理候选: 直接输出代理响应  
        3. 混合候选: 10秒超时机制
        """
        try:
            # 1. 智能预测下一个发言者
            next_speaker = self._meta_planner_select_speaker(user_input)
            print(f"Meta Planner: 预测发言者 -> {next_speaker}")
            
            # 2. 分析发言者类型并应用对应的等待策略
            speaker_candidates = self._analyze_speaker_candidates(user_input, next_speaker)
            print(f"Meta Planner: 发言者候选分析 -> {speaker_candidates}")
        except Exception as e:
            print(f"Meta Planner: 发言者选择过程出错 -> {e}")
            raise e
        
        if speaker_candidates['type'] == 'user_only':
            # 仅用户候选 - 无限等待
            return {
                'type': 'wait_for_user',
                'wait_strategy': 'infinite',
                'message': '请继续您的想法...',
                'current_stage': self.get_current_stage_name(),
                'meta_planner_status': '等待用户输入（无限等待）',
                'next_speaker_info': speaker_candidates
            }
            
        elif speaker_candidates['type'] == 'agent_only':
            # 仅代理候选 - 直接输出响应
            try:
                # 如果有明确指定的target_agent，使用它；否则使用预测的next_speaker
                actual_speaker = speaker_candidates.get('target_agent', next_speaker)
                print(f"Meta Planner: 实际发言者 -> {actual_speaker}")

                if not actual_speaker:
                    raise ValueError("actual_speaker is None or empty")

                response = self._generate_character_response(actual_speaker, user_input)
                speaker_name = self.agents[actual_speaker]['name']

                # 记录到对话历史
                self.conversation_history.append({
                    'speaker': speaker_name,
                    'message': response,
                    'timestamp': time.time()
                })

                return {
                    'speaker': speaker_name,
                    'message': response
                }
            except Exception as e:
                print(f"Meta Planner: agent_only分支处理出错 -> {e}")
                # Fallback response
                return {
                    'speaker': 'System',
                    'message': 'Sorry, an error occurred while generating a response.'
                }

        else:  # mixed_candidates
            # 混合候选（用户+代理）- 10秒超时等待
            return {
                'type': 'mixed_wait',
                'wait_strategy': 'timeout_10s',
                'next_speaker': next_speaker,
                'message': '您可以继续发言，或等待其他同学回应...',
                'current_stage': self.get_current_stage_name(),
                'meta_planner_status': f'混合等待（10秒超时），候选: 用户 + {next_speaker.replace("mathvc_", "").capitalize()}',
                'timeout_fallback_speaker': next_speaker
            }
    
    def _analyze_speaker_candidates(self, user_input: str, predicted_speaker: str) -> Dict[str, Any]:
        """
        分析发言者候选情况 - 实现论文第327-338行的候选判定逻辑
        """
        # 优先检查是否明确指向特定代理（最高优先级）
        direct_mention = self._detect_direct_mention(user_input)
        if direct_mention:
            return {
                'type': 'agent_only',
                'target_agent': direct_mention,
                'reason': '明确指名特定角色'
            }
        
        # 检查是否明确指向用户继续发言（仅在没有直接指名时）
        user_continue_patterns = [
            "你觉得呢", "你的想法", "你认为", "继续说", "还有吗", "你怎么看"
        ]
        
        if any(pattern in user_input for pattern in user_continue_patterns):
            return {
                'type': 'user_only',
                'reason': '用户被明确邀请继续发言'
            }
        
        # 检查对话阶段和上下文
        recent_speakers = [msg['speaker'] for msg in self.conversation_history[-3:] if msg['speaker'] != '用户']
        
        # 如果用户刚刚发言，通常应该有代理回应
        if len(self.conversation_history) > 0 and self.conversation_history[-1]['speaker'] == '用户':
            return {
                'type': 'agent_only',
                'target_agent': predicted_speaker,
                'reason': '用户发言后需要代理回应'
            }
        
        # 如果代理刚刚发言，根据论文设计进行智能分配
        if len(self.conversation_history) > 0 and self.conversation_history[-1]['speaker'] != '用户':
            last_speaker = self.conversation_history[-1]['speaker']
            
            # 检查是否需要继续代理间讨论
            agent_discussion_needed = self._should_continue_agent_discussion(last_speaker, recent_speakers)
            
            if agent_discussion_needed:
                # 代理继续讨论 - 选择下一个代理
                next_agent = self._select_next_agent_for_discussion(last_speaker)
                return {
                    'type': 'agent_only',
                    'target_agent': next_agent,
                    'reason': '代理间继续讨论'
                }
            else:
                # 混合候选：用户可以参与，或10秒后代理继续
                return {
                    'type': 'mixed_wait',
                    'user_candidate': True,
                    'agent_candidate': predicted_speaker,
                    'reason': '等待用户参与或代理继续',
                    'timeout_seconds': 10
                }
        
        # 默认情况：混合候选（用户+代理都可以发言）
        return {
            'type': 'mixed_wait',
            'user_candidate': True,
            'agent_candidate': predicted_speaker,
            'reason': '开放式讨论阶段',
            'timeout_seconds': 10
        }
    
    def _meta_planner_select_speaker(self, user_input: str) -> str:
        """
        Meta Planner的Dialogue Control组件 - 严格按照论文第319-326行实现
        基于对话上下文智能预测下一个发言者
        """
        # 1. 直接指名检测（论文示例："Hey Bob, you made a mistake..."）
        if self._detect_direct_mention(user_input):
            return self._detect_direct_mention(user_input)
        
        # 2. 基于对话上下文的智能预测
        return self._predict_next_speaker_from_context(user_input)
    
    def _detect_direct_mention(self, user_input: str) -> str:
        """检测用户是否直接指名某个角色"""
        user_input_lower = user_input.lower()
        
        # 检测各种指名模式
        name_patterns = {
            "alice": ["alice", "爱丽丝", "alice，", "alice,", "alice你", "alice怎么"],
            "bob": ["bob", "鲍勃", "bob，", "bob,", "bob你", "bob怎么"],
            "charlie": ["charlie", "查理", "charlie，", "charlie,", "charlie你", "charlie怎么"]
        }
        
        for agent_key, patterns in name_patterns.items():
            for pattern in patterns:
                if pattern in user_input_lower:
                    return f"mathvc_{agent_key}"
        
        # 检测错误指正模式（论文示例："Hey Bob, you made a mistake..."）
        mistake_patterns = [
            "你错了", "你搞错了", "不对", "有错误", "mistake", "wrong", "错误"
        ]
        
        for pattern in mistake_patterns:
            if pattern in user_input_lower:
                # 找到最近发言的角色
                last_agent = self._get_last_agent_speaker()
                if last_agent:
                    return last_agent
        
        return None
    
    def _predict_next_speaker_from_context(self, user_input: str) -> str:
        """
        基于对话上下文预测下一个发言者 - 融合原系统优秀实现
        论文第319-326行智能发言者预测
        """
        if not self.conversation_history:
            return "mathvc_alice"  # 默认从Alice开始
        
        # 获取最近的对话上下文（融合原系统方法）
        recent_messages = self.conversation_history[-3:] if len(self.conversation_history) >= 3 else self.conversation_history
        recent_context = "\n".join([f"{msg['speaker']}: {msg['message']}" for msg in recent_messages])
        
        prompt = f"""
        基于以下对话历史，智能预测下一个最合适的发言者。
        
        当前协作阶段：{self.get_current_stage_name()}
        
        最近对话：
        {recent_context}
        
        用户输入：{user_input}
        
        可选发言者：Alice（数学能力较差）, Bob（数学能力中等）, Charlie（数学能力较好）
        
        分析规则（融合原系统优秀逻辑）：
        1. 如果有人被直接提及或询问（如"Hey Bob"），那个人应该回应
        2. 如果有人提出了错误，其他人应该指出或讨论
        3. 如果需要计算验证，Charlie（能力较好）更适合
        4. 如果需要提问澄清，Alice（能力较差）更适合
        5. 如果讨论了复杂概念，能力较好的学生更可能发言
        6. 在团队组织阶段，不同学生会主动承担不同任务
        7. 考虑对话的自然流动和角色特点
        
        请只输出一个名字：Alice, Bob, 或 Charlie
        """
        
        try:
            response = self._call_llm(prompt, temperature=0.3, max_tokens=50)
            response = response.strip().lower()
            
            if "alice" in response:
                return "mathvc_alice"
            elif "bob" in response:
                return "mathvc_bob"
            elif "charlie" in response:
                return "mathvc_charlie"
            else:
                # 如果LLM响应不明确，使用简单轮流机制作为后备（原系统策略）
                agents = ["mathvc_alice", "mathvc_bob", "mathvc_charlie"]
                if hasattr(self, 'current_speaker') and self.current_speaker in agents:
                    current_index = agents.index(self.current_speaker)
                    next_index = (current_index + 1) % len(agents)
                    return agents[next_index]
                else:
                    return "mathvc_alice"
        except Exception as e:
            print(f"预测发言者时出错: {e}")
            # 出错时使用简单轮流机制（原系统策略）
            agents = ["mathvc_alice", "mathvc_bob", "mathvc_charlie"]
            if hasattr(self, 'current_speaker') and self.current_speaker in agents:
                current_index = agents.index(self.current_speaker)
                next_index = (current_index + 1) % len(agents)
                return agents[next_index]
            else:
                return "mathvc_alice"
    
    def _get_last_agent_speaker(self) -> str:
        """获取最近发言的代理角色"""
        for msg in reversed(self.conversation_history):
            speaker = msg.get('speaker', '')
            if speaker in ['Alice', 'Bob', 'Charlie']:
                return f"mathvc_{speaker.lower()}"
        return None
    
    def _get_recent_conversation_context(self) -> str:
        """获取最近的对话上下文"""
        recent_messages = self.conversation_history[-5:] if len(self.conversation_history) >= 5 else self.conversation_history
        context = ""
        for msg in recent_messages:
            speaker = msg.get('speaker', '')
            message = msg.get('message', '')
            context += f"{speaker}: {message}\n"
        return context
    
    def _determine_next_speaker(self) -> str:
        """基于对话历史智能选择下一个发言者"""
        if not self.conversation_history:
            return "mathvc_alice"
        
        # 获取最近的发言者
        recent_speakers = [msg['speaker'] for msg in self.conversation_history[-3:] if msg['speaker'] != '用户']
        
        # 避免同一角色连续发言
        if recent_speakers:
            last_speaker = recent_speakers[-1]
            available_agents = ["mathvc_alice", "mathvc_bob", "mathvc_charlie"]
            
            # 移除最近发言的角色
            if last_speaker == "Alice":
                available_agents.remove("mathvc_alice")
            elif last_speaker == "Bob":
                available_agents.remove("mathvc_bob")
            elif last_speaker == "Charlie":
                available_agents.remove("mathvc_charlie")
            
            if available_agents:
                return random.choice(available_agents)
        
        return random.choice(["mathvc_alice", "mathvc_bob", "mathvc_charlie"])
    
    def _generate_character_response(self, agent_name: str, user_input: str) -> str:
        """生成角色响应 - 融合原系统优秀的两步响应生成方法"""
        # This method is now the entry point for the two-step generation
        dialogue_act = self._generate_dialogue_act(agent_name, user_input)
        return self._generate_character_schema_based_response(agent_name, dialogue_act)
    
    def _generate_dialogue_act(self, agent_name: str, user_input: str) -> str:
        """
        Generates a dialogue act for the character based on the current context.
        """
        character_schema_str = json.dumps(self.character_schemas.get(agent_name, {}), indent=4)
        agent_info = self.agents[agent_name]
        recent_context = self._get_recent_conversation_context()

        # Define dialogue acts based on the current stage
        stage_dialogue_acts = {
            "problem_understanding": ["present a task understanding", "ask for a clarifying question", "agree with a teammate", "disagree with a teammate"],
            "modeling": ["propose a modeling plan", "ask about a modeling detail", "suggest a different model"],
            "calculation": ["state a calculation result", "ask for help with a calculation", "double-check a calculation"],
            "validation": ["confirm a result", "question a result", "propose a validation method"],
            "summary": ["summarize the solution", "reflect on the process", "ask about the final answer"]
        }
        current_stage_name = self.get_current_stage()
        available_acts = stage_dialogue_acts.get(current_stage_name, ["say something"])

        prompt = f"""
        You are simulating a middle school student named {agent_info['name']} with a {agent_info['math_level']} math level.
        Your current understanding of the problem is represented by this schema:
        {character_schema_str}

        Here is the recent conversation:
        {recent_context}

        Based on the current situation and your personality, choose the most appropriate dialogue act from the following list:
        {available_acts}

        Your chosen act should be a short phrase describing your intent. For example: 'ask for a clarifying question about the total cost'.
        Please only output the dialogue act phrase.
        """
        
        try:
            dialogue_act = self._call_llm(prompt, temperature=0.8, max_tokens=100)
            return dialogue_act.strip()
        except Exception as e:
            print(f"Error generating dialogue act for {agent_name}: {e}")
            return "state a simple opinion"

    def _generate_character_schema_based_response(self, agent_name: str, dialogue_act: str) -> str:
        """Generates a character response based on their schema and a dialogue act."""
        character_schema_str = json.dumps(self.character_schemas.get(agent_name, {}), indent=4)
        agent_info = self.agents[agent_name]
        recent_context = self._get_recent_conversation_context()

        prompt = f"""
        You are a middle school student named {agent_info['name']}.
        - Your math skill level is: {agent_info['math_level']}
        - Your personality is: {agent_info['personality']}

        Here is your current understanding of the math problem (it might contain errors):
        {character_schema_str}

        Here is the recent conversation:
        {recent_context}

        Your assigned task is to perform the following dialogue act: "{dialogue_act}"

        Based on your character, your understanding of the problem (your schema), and the dialogue act, please generate a short, natural-sounding response in the first person, as if you were this student.
        Keep your response colloquial and to the point.
        """

        try:
            response = self._call_llm(prompt, temperature=0.85, max_tokens=200)
            # In a future step, we could re-implement schema modification based on the response.
            return response.strip()
        except Exception as e:
            print(f"Error in response generation for {agent_name}: {e}")
            return "Uh... I'm not sure what to say."

    def _update_character_schema_based_on_response(self, agent_name: str, response: str):
        """基于响应更新角色模式（模拟思维演进）- 融合原系统优秀实现"""
        try:
            # 简单的模式更新：记录最近的回应风格
            if agent_name in self.character_schemas:
                if 'recent_responses' not in self.character_schemas[agent_name]:
                    self.character_schemas[agent_name]['recent_responses'] = []
                
                self.character_schemas[agent_name]['recent_responses'].append(response)
                
                # 只保留最近3次回应
                if len(self.character_schemas[agent_name]['recent_responses']) > 3:
                    self.character_schemas[agent_name]['recent_responses'] = \
                        self.character_schemas[agent_name]['recent_responses'][-3:]
                        
                print(f"Meta Planner: 已更新{agent_name}的Character Schema")
        except Exception as e:
            print(f"更新角色模式时出错: {e}")
    
    def _update_character_schemas_based_on_input(self, user_input: str):
        """基于用户输入更新Character Schemas"""
        print(f"Meta Planner: 基于用户输入更新Character Schemas: {user_input}")
        
        # 根据用户输入调整各角色的理解
        for agent_name in self.character_schemas:
            if agent_name in self.character_schemas:
                self.character_schemas[agent_name]["last_user_input"] = user_input
                self.character_schemas[agent_name]["updated_at"] = time.time()
    
    def _check_stage_transition(self):
        """Collaboration Stage Monitor - 检查协作阶段是否需要推进"""
        current_stage = self.get_current_stage()
        conversation_length = len(self.conversation_history)
        
        # 简单的阶段推进逻辑 - 可以根据对话内容智能判断
        if conversation_length > 5 and current_stage == "problem_understanding":
            self.current_stage_index = 1  # 推进到建模阶段
            print("Meta Planner: 协作阶段推进到建模阶段")
        elif conversation_length > 10 and current_stage == "modeling":
            self.current_stage_index = 2  # 推进到计算阶段
            print("Meta Planner: 协作阶段推进到计算阶段")
        elif conversation_length > 15 and current_stage == "calculation":
            self.current_stage_index = 3  # 推进到验证阶段
            print("Meta Planner: 协作阶段推进到验证阶段")
        elif conversation_length > 20 and current_stage == "validation":
            self.current_stage_index = 4  # 推进到总结阶段
            print("Meta Planner: 协作阶段推进到总结阶段")
    
    def get_current_stage(self) -> str:
        """获取当前协作阶段"""
        if self.current_stage_index < len(self.COLLABORATION_STAGES):
            return self.COLLABORATION_STAGES[self.current_stage_index]
        return self.COLLABORATION_STAGES[-1]
    
    def get_current_stage_name(self) -> str:
        """获取当前协作阶段名称"""
        stage = self.get_current_stage()
        return self.STAGE_NAMES.get(stage, stage)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history
    
    def _call_llm(self, prompt: str, temperature: float = 0.7, max_tokens: int = 200) -> str:
        """调用Qwen LLM API with retry logic"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        api_url = f"{self.api_base_url}/chat/completions"
        retries = 3
        delay = 5  # Start with a 5-second delay

        for attempt in range(retries):
            try:
                response = requests.post(api_url, headers=headers, json=data, timeout=60)
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content']
                else:
                    print(f"LLM API response format error: {result}")
                    # Don't retry on format errors, return a default message
                    return "Sorry, I received an unusual response."

            except requests.exceptions.HTTPError as e:
                # Retry on 429 (Too Many Requests) and 5xx server errors
                if e.response.status_code == 429 or e.response.status_code >= 500:
                    print(f"API error: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    print(f"HTTP error: {e}")
                    return "Sorry, a connection error occurred."
            except requests.exceptions.RequestException as e:
                print(f"LLM API call failed: {e}")
                return "Sorry, there was a network connection issue."
            except Exception as e:
                print(f"An unknown error occurred during LLM call: {e}")
                return "Sorry, a technical problem occurred."

        print("LLM call failed after multiple retries.")
        return "Sorry, the service is currently unavailable. Please try again later."
    
    def _monitor_collaboration_stage(self):
        """
        监控协作阶段推进 - 基于论文的五阶段协作模型
        根据对话内容和进度自动推进协作阶段
        """
        if not self.conversation_history:
            return
        
        # 分析最近的对话内容，判断是否需要推进到下一阶段
        recent_messages = self.conversation_history[-5:]  # 分析最近5条消息
        
        # 获取当前阶段
        current_stage = self.COLLABORATION_STAGES[self.current_stage_index]
        
        # 根据对话内容判断是否应该推进阶段
        stage_keywords = {
            "problem_understanding": ["理解", "问题", "什么意思", "明白"],
            "modeling": ["建模", "公式", "方程", "模型", "设定"],
            "calculation": ["计算", "算", "结果", "答案", "数字"],
            "validation": ["检验", "验证", "对不对", "正确", "错误"],
            "summary": ["总结", "结论", "最后", "综上"]
        }
        
        # 检查是否有足够的讨论内容推进到下一阶段
        if len(recent_messages) >= 3:  # 至少有3条消息后才考虑推进
            # 简单的阶段推进逻辑：如果当前不是最后阶段，且有一定的讨论量，就推进
            if self.current_stage_index < len(self.COLLABORATION_STAGES) - 1:
                # 检查是否有足够的角色参与
                speakers_in_recent = set(msg.get('speaker', '') for msg in recent_messages)
                if len(speakers_in_recent) >= 2:  # 至少有2个不同的发言者
                    self.current_stage_index += 1
                    new_stage = self.COLLABORATION_STAGES[self.current_stage_index]
                    print(f"协作阶段推进: {current_stage} -> {new_stage}")
    
    def get_current_stage_name(self):
        """获取当前阶段的中文名称"""
        if self.current_stage_index < len(self.COLLABORATION_STAGES):
            stage_key = self.COLLABORATION_STAGES[self.current_stage_index]
            return self.STAGE_NAMES.get(stage_key, stage_key)
        return "未知阶段"
    
    def get_conversation_history(self):
        """获取对话历史"""
        return self.conversation_history
