import json
import sys
import time
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient
import model

ChannelFactoryInitialize(0, "en7")
sport_client = SportClient()
sport_client.SetTimeout(10.0)
sport_client.Init()

api_methods = {
    "Damp": sport_client.Damp,
    "BalanceStand": sport_client.BalanceStand,
    "StopMove": sport_client.StopMove,
    "StandUp": sport_client.StandUp,
    "StandDown": sport_client.StandDown,
    "RecoveryStand": sport_client.RecoveryStand,
    "Move": sport_client.Move,
    "SpeedLevel": sport_client.SpeedLevel,
    "ContinuousGait": sport_client.ContinuousGait,
    "FrontFlip": sport_client.FrontFlip,
    "TrajectoryFollow": sport_client.TrajectoryFollow,
    "Euler": sport_client.Euler,
    "Sit": sport_client.Sit,
    "RiseSit": sport_client.RiseSit,
    "SwitchGait": sport_client.SwitchGait,
    "BodyHeight": sport_client.BodyHeight,
    "FootRaiseHeight": sport_client.FootRaiseHeight,
    "Hello": sport_client.Hello,
    "Stretch": sport_client.Stretch,
    "SwitchJoystick": sport_client.SwitchJoystick,
    "Wallow": sport_client.Wallow,
    "Pose": sport_client.Pose,
    "Scrape": sport_client.Scrape,
    "FrontJump": sport_client.FrontJump,
    "FrontPounce": sport_client.FrontPounce,
    "Dance1": sport_client.Dance1,
    "Dance2": sport_client.Dance2,
    "GetState": sport_client.GetState,
}

api_params = {
    "Damp": {},
    "BalanceStand": {},
    "StopMove": {},
    "StandUp": {},
    "StandDown": {},
    "RecoveryStand": {},
    "Move": {"vx": float, "vy": float, "vyaw": float},
    "SpeedLevel": {"level": int},
    "ContinuousGait": {"flag": bool},
    "FrontFlip": {},
    "TrajectoryFollow": {"path": list},  # 此处简化处理，实际需将列表转换为PathPoint对象列表
    "Euler": {"roll": float, "pitch": float, "yaw": float},
    "Sit": {},
    "RiseSit": {},
    "SwitchGait": {"d": int},
    "BodyHeight": {"height": float},
    "FootRaiseHeight": {"height": float},
    "Hello": {},
    "Stretch": {},
    "SwitchJoystick": {"flag": bool},
    "Wallow": {},
    "Pose": {"flag": bool},
    "Scrape": {},
    "FrontJump": {},
    "FrontPounce": {},
    "Dance1": {},
    "Dance2": {},
    "GetState": {"_vector": list, "_map": dict},
}

def process_json_command(json_data):
    # 检查是否包含必须字段
    required_keys = ["action_queue", "safety_checks", "execution_priority"]
    for key in required_keys:
        if key not in json_data:
            print(f"错误：缺少字段 {key}")
            return

    # 安全检查
    safety = json_data["safety_checks"]
    if not (safety.get("environment_safe") and safety.get("motion_feasible")):
        print("安全检查未通过，请检查环境安全与运动可行性！")
        return

    results = []
    # 遍历动作队列，按顺序执行各接口
    for action in json_data["action_queue"]:
        api_name = action.get("api_name")
        parameters = action.get("parameters", {})
        reason = action.get("reason", "")
        expected_outcome = action.get("expected_outcome", "")

        if api_name not in api_methods:
            msg = f"未找到对应接口: {api_name}"
            print(msg)
            results.append({
                "api_name": api_name,
                "status": "failed",
                "message": msg
            })
            continue

        # 校验并转换参数
        expected_params = api_params.get(api_name, {})
        call_params = {}
        valid_params = True
        for param, param_type in expected_params.items():
            if param not in parameters:
                msg = f"接口 {api_name} 缺少参数: {param}"
                print(msg)
                results.append({
                    "api_name": api_name,
                    "status": "failed",
                    "message": msg
                })
                valid_params = False
                break
            else:
                try:
                    value = parameters[param]
                    # 对布尔类型做特殊处理
                    if param_type == bool:
                        if isinstance(value, bool):
                            call_params[param] = value
                        elif isinstance(value, str):
                            call_params[param] = (value.lower() == "true")
                        else:
                            call_params[param] = bool(value)
                    else:
                        call_params[param] = param_type(value)
                except Exception as e:
                    msg = f"接口 {api_name} 参数 {param} 类型转换错误: {str(e)}"
                    print(msg)
                    results.append({
                        "api_name": api_name,
                        "status": "failed",
                        "message": msg
                    })
                    valid_params = False
                    break

        if not valid_params:
            continue

        # 执行对应接口
        try:
            if call_params:
                print(f"执行接口: {api_name} 参数: {call_params} (原因: {reason})")
                api_methods[api_name](**call_params)
            else:
                print(f"执行接口: {api_name} (无参数) (原因: {reason})")
                sport_client.StandUp()
                api_methods[api_name]()

            results.append({
                "api_name": api_name,
                "status": "executed",
                "message": f"{expected_outcome} (原因: {reason})",
                "parameters": call_params
            })
        except Exception as e:
            msg = f"执行接口 {api_name} 异常: {str(e)}"
            print(msg)
            results.append({
                "api_name": api_name,
                "status": "failed",
                "message": msg
            })

    return results

# 主逻辑：从文件或标准输入读取 JSON 数据，并执行动作队列
if __name__ == '__main__':
    while True:
        model.main()
        json_filename = "action.json"
        try:
            with open(json_filename, "r", encoding="utf-8") as f:
                json_data = json.load(f)
        except Exception as e:
            print(f"读取文件 {json_filename} 失败: {str(e)}")
            sys.exit(1)

        results = process_json_command(json_data)
        print("\n处理结果：")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        time.sleep(0.5)