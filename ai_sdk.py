Damp() #进入阻尼状态。参数	无
BalanceStand() #解除锁定。参数	无
StopMove() #停下当前动作，将绝大多数指令恢复成默认值。参数 无
StandUp() #关节锁定，站高。参数	无
StandDown() #关节锁定，站低。参数	无
RecoveryStand() #恢复站立。参数	无
Move(float vx, float vy, float vyaw) #移动。
#参数 vx: [-0.6~0.6] (m/s)； vy: [-0.4~0.4] (m/s)； vyaw: [-0.8~0.8] (rad/s)。
SpeedLevel(int level) #设置速度档位。
#参数 level：速度档位枚举值，取值  -1  为慢速，1  为快速。
ContinuousGait(bool flag) #持续移动。
#参数 flag：设置 true  为开启，false  为关闭。
MoveToPos(float x, float y, float yaw) #移动到里程计坐标系中指定位置。
#参数 x: 里程计坐标系中的x，单位m；y: 里程计坐标系中的y，单位m；yaw: 里程计坐标系中的偏航角，单位rad，建议取值范围-3.14～3.14。
HandStand(bool flag) #倒立行走。
#参数 flag：设置 true  为开启，false  为关闭。
FrontFlip() #前空翻。参数 无。
SwitchMoveMode(bool flag) #切换Move()响应模式。
#参数 flag：设置 true  开启Move()持续响应模式，在运动模式下，会一直响应最新的Move指令。false  为关闭Move()持续响应模式，如果未收到新的Move指令，会延迟1s后自动停止。
TrajectoryFollow(std::vector< PathPoint >& path) #轨迹跟踪。
#参数 path 是机器狗在未来一段时间内的目标运动轨迹，它由 30 个轨迹点 PathPoint 组成。
LeftFlip() #左空翻。参数 无。
BackFlip() #后空翻。参数 无。
FreeWalk() #灵动模式。参数 无。
FreeBound(bool flag) #并腿跑模式。
#参数 flag：设置true，进入并腿跑；设置false，退出并腿跑，进入灵动。
FreeJump(bool flag) #跳跃模式。
#参数 flag：设置true，进入跳跃模式；设置false，退出跳跃模式，进入灵动。
FreeAvoid(bool flag) #闪避模式。
#参数 flag：设置true，进入闪避模式；设置false，退出闪避模式，进入灵动。
WalkStair(bool flag) #爬楼梯模式。
#参数 flag：设置true，进入爬楼梯模式；设置false，退出爬楼梯模式，进入灵动。
WalkUpright(bool flag) #后腿直立模式。
#参数 flag：设置true，进入后腿直立模式；设置false，退出后腿直立模式，进入灵动。
CrossStep(bool flag) #交叉步模式。
#参数 flag：设置true，进入交叉步模式；设置false，退出交叉步模式，进入灵动。

[
    {
        "tool_name_1": tool_name_1->str,
        "args": {
            # 当前工具对应的必填参数
            "arg_1_name": arg_1_value->str/int/float/bool,
            "arg_2_name": arg_2_value->str/int/float/bool,
        },
        # 描述当前决策的因果逻辑.
        "decision_reason": decision_reason->str
    },
    {
        "tool_name_2": tool_name_2->str,
        "args": {
        
        },
        "decision_reason": decision_reason->str
    }
]






