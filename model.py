import pandas as pd
from zhipuai import ZhipuAI
import base64
import random
import json
import cv2
import capture_image

df = pd.read_csv("接口表.csv")

# 生成格式化的API文档
api_doc = "可用的API接口列表：\n\n"

for index, row in df.iterrows():
    api_doc += f"【接口名称】{row['接口名']}\n"
    
    # 处理参数
    try:
        params = eval(row['接口参数'])
        if isinstance(params, dict):
            if "参数名" in params and params["参数名"] == "无":
                param_str = "无参数"
            else:
                param_list = []
                for param_name, param_type in params.items():
                    if param_name not in ["参数名", "参数数值类型"]:
                        param_list.append(f"{param_name}: {param_type}")
                param_str = ", ".join(param_list)
    except:
        param_str = "参数解析错误"
    
    api_doc += f"【参数说明】{param_str}\n"
    api_doc += f"【接口功能】{row['接口含义']}\n"
    api_doc += f"【使用场景】{row['适用场景']}\n"
    api_doc += "----------------------------------------\n"

prompt = """你已经被装在在了宇树科技的GO2机器人上。你需要基于输入的多模态信息，为自己生成行为决策序列。请严格按照可用的SDK API接口进行规划。

当前可用的所有API接口如下：
<tool-use>
$$$api_doc$$$
</tool-use>

系统输入信息包括：
1. 视觉信息 (base64_str): [多模态输入-图像]
2. 当前姿态信息 (current_gesture_info): [当前姿态数据-传感器]
3. 当前运动信息 (current_motion_info): [当前运动数据-传感器]
4. 当前状态信息 (current_state_info): [当前状态数据-内部信息]
5. 当前指令 (current_following_instruction): [当前用户指令-外部信息]
6. 历史记录 (previous_history): [历史行为-前序决策]

请你执行以下分析步骤：

1. 环境感知分析
- 分析当前场景中的关键物体和空间关系
- 识别潜在的障碍物和安全风险
- 评估执行指令的环境可行性

2. 状态评估
- 评估机器人当前姿态是否适合执行新指令
- 检查是否需要进行姿态调整
- 确认当前状态下可执行的动作范围

3. 指令解析
- 理解用户指令的具体要求
- 将指令分解为可执行的基本动作
- 确定动作的优先级和依赖关系

请按照以下JSON格式输出行为决策序列：
{
    "action_queue": [
        {
            "api_name": "接口名称",
            "parameters": {
                "参数名": "参数值"
            },
            "reason": "调用原因说明",
            "expected_outcome": "预期结果"
        }
    ],
    "safety_checks": {
        "environment_safe": true/false,
        "motion_feasible": true/false,
        "risk_assessment": "风险评估说明"
    },
    "execution_priority": "normal/high/emergency"
}

注意事项：
1. 所有API调用必须严格遵循提供的接口规范
2. 优先考虑机器人和环境的安全性
3. 确保动作序列的连贯性和平滑过渡
4. 在遇到异常情况时应包含适当的恢复策略"""

prompt = prompt.replace("$$$api_doc$$$", api_doc)

# def sample_random_frame_base64(video_path):
#     """
#     从视频文件中随机采样一帧并返回base64格式
    
#     参数:
#         video_path (str): 视频文件的路径
    
#     返回:
#         base64_str: base64编码的图像字符串
#         frame_number: 采样的帧号
#     """
#     try:
#         # 打开视频文件
#         cap = cv2.VideoCapture(video_path)
        
#         if not cap.isOpened():
#             print("Error: 无法打开视频文件")
#             return None, -1
        
#         # 获取视频总帧数
#         total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
#         if total_frames <= 0:
#             print("Error: 视频帧数为0")
#             return None, -1
        
#         # 随机选择一个帧号
#         random_frame = random.randint(0, total_frames - 1)
        
#         # 设置视频读取位置到随机帧
#         cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame)
        
#         # 读取该帧
#         ret, frame = cap.read()
        
#         # 释放视频对象
#         cap.release()
        
#         if ret:
#             # 将帧编码为jpg格式
#             _, buffer = cv2.imencode('.jpg', frame)
#             # 直接将buffer转换为base64字符串
#             base64_str = base64.b64encode(buffer).decode('utf-8')
#             return base64_str, random_frame
#         else:
#             print("Error: 无法读取选中的帧")
#             return None, -1
            
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None, -1

def the_big_brain(base64_str,
    current_following_instruction="起立", 
    current_gesture_info = """
    IMU Roll/Pitch/Yaw: (0.0058678435161709785, -0.10672464966773987, -0.02628220058977604)
    Front right hip angle: -0.34
    """,
    current_motion_info = """
    """,
    current_state_info = """
    Robot connected: True
    Battery voltage: 29.42V
    """, 
    previous_history = """"""):
    
    client = ZhipuAI(api_key="9417cf90b6934c2baee41d6ce508c28b.FWXcf3bLG6CVZeis", timeout=10)
    
    curr_info = f"""
    <gesture_info>
    {current_gesture_info.strip()}
    </gesture_info>
    <motion_info>
    {current_motion_info.strip()}
    </motion_info>
    <state_info>
    {current_state_info.strip()}
    </state_info>
    <history>
    {previous_history.strip()}
    </history>
    """

    response = client.chat.completions.create(
        model="glm-4v-plus",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_str  # 直接使用base64字符串
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "text",
                        "text": f"<user_instruction>{current_following_instruction}</user_instruction>\n{curr_info}"
                    },
                ]
            }
        ]
    )

    return response.choices[0].message.content

# 使用示例
capture_image.capture_image()
# 读取图片并转换成 base64 编码字符串
with open("img.jpg", "rb") as img_file:
    base64_str = base64.b64encode(img_file.read()).decode("utf-8")
api_output = the_big_brain(base64_str)
print(api_output)

def validate_model_output(response_json, api_doc):
    """
    验证模型输出的JSON格式和内容是否合法
    
    参数:
        response_json (dict): 模型输出的JSON对象
        api_doc (str): API文档字符串
    
    返回:
        tuple: (is_valid, message)
    """
    # 验证基本结构
    required_keys = ["action_queue", "safety_checks", "execution_priority"]
    for key in required_keys:
        if key not in response_json:
            return False, f"缺少必需字段: {key}"
    
    # 验证execution_priority
    valid_priorities = ["normal", "high", "emergency"]
    if response_json["execution_priority"] not in valid_priorities:
        return False, f"无效的execution_priority值: {response_json['execution_priority']}"
    
    # 验证safety_checks结构
    safety_checks = response_json["safety_checks"]
    required_safety_keys = ["environment_safe", "motion_feasible", "risk_assessment"]
    for key in required_safety_keys:
        if key not in safety_checks:
            return False, f"safety_checks缺少必需字段: {key}"
    
    # 验证safety_checks的数据类型
    if not isinstance(safety_checks["environment_safe"], bool):
        return False, "environment_safe必须是布尔值"
    if not isinstance(safety_checks["motion_feasible"], bool):
        return False, "motion_feasible必须是布尔值"
    if not isinstance(safety_checks["risk_assessment"], str):
        return False, "risk_assessment必须是字符串"
    
    # 解析API文档以获取可用的API列表
    available_apis = []
    current_api = {}
    for line in api_doc.split('\n'):
        if "【接口名称】" in line:
            if current_api:
                available_apis.append(current_api)
            current_api = {'name': line.replace("【接口名称】", "").strip()}
        elif "【参数说明】" in line and current_api:
            current_api['params'] = line.replace("【参数说明】", "").strip()
    if current_api:
        available_apis.append(current_api)
    
    # 验证action_queue中的每个动作
    for action in response_json["action_queue"]:
        # 验证动作结构
        required_action_keys = ["api_name", "parameters", "reason", "expected_outcome"]
        for key in required_action_keys:
            if key not in action:
                return False, f"动作缺少必需字段: {key}"
        
        # 验证API调用
        is_valid, message = validate_api_call(
            action["api_name"],
            action["parameters"],
            available_apis
        )
        if not is_valid:
            return False, f"API调用验证失败: {message}"
    
    return True, "验证通过"

def validate_api_call(api_name, parameters, available_apis):
    """验证单个API调用是否合法"""
    # 检查API是否存在
    api_info = None
    for api in available_apis:
        if api['name'] == api_name:
            api_info = api
            break
    
    if not api_info:
        return False, f"API '{api_name}' 不存在"
    
    # 检查参数
    try:
        param_str = api_info['params']
        # 处理"无参数"的特殊情况
        if param_str == "无参数" or param_str == '{"参数名": "无", "参数数值类型": "无"}':
            if parameters and len(parameters) > 0:
                return False, f"API '{api_name}' 不需要参数，但提供了参数"
            return True, "验证通过"
            
        # 处理有参数的情况
        expected_params = eval(param_str)
        # 检查必需参数是否都存在
        for param_name, param_type in expected_params.items():
            if param_name not in ["参数名", "参数数值类型"]:
                if param_name not in parameters:
                    return False, f"API '{api_name}' 缺少必需参数 '{param_name}'"
                
                # 检查参数类型
                if param_type == "float":
                    try:
                        float(parameters[param_name])
                    except:
                        return False, f"参数 '{param_name}' 应为浮点数"
                elif param_type == "int":
                    try:
                        int(parameters[param_name])
                    except:
                        return False, f"参数 '{param_name}' 应为整数"
                elif param_type == "bool":
                    if not isinstance(parameters[param_name], bool):
                        return False, f"参数 '{param_name}' 应为布尔值"
                        
    except Exception as e:
        return False, f"参数验证失败: {str(e)}"
    
    return True, "验证通过"

def process_model_response(response_text, api_doc):
    """处理模型响应"""
    response_text = response_text.strip("```json").strip("```")
    try:
        # 尝试解析JSON
        if isinstance(response_text, str):
            response_json = json.loads(response_text)
        else:
            response_json = response_text
            
        # 验证输出
        is_valid, message = validate_model_output(response_json, api_doc)
        
        if not is_valid:
            print(f"验证失败: {message}")
            return None
        
        print("验证通过，输出有效")
        return response_json
        
    except json.JSONDecodeError:
        print("JSON解析失败")
        return None
    except Exception as e:
        print(f"处理失败: {str(e)}")
        return None

validated_response = process_model_response(api_output, api_doc)

if validated_response:
    # 处理验证通过的响应
    action_queue = validated_response["action_queue"]
    for action in action_queue:
        # 执行动作
        print(f"执行动作: {action['api_name']}")
else:
    # 处理验证失败的情况
    print("响应验证失败，需要重新生成")
    