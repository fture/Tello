import cv2
from cvzone.HandTrackingModule import HandDetector
from djitellopy import Tello
import time

# 初始化手部检测器
detectorHand = HandDetector(maxHands=2, detectionCon=0.7)  # 提高手识别的可信度

# 初始化 Tello 无人机
tello = Tello()
tello.connect()
print(f"Battery Life Percentage: {tello.get_battery()}%")

tello.streamon()

# 初始化速度变量
lr, fb, ud, yaw = 0, 0, 0, 0
speed = 30  # 设置无人机移动速度
yaw_speed = 30  # 设置无人机回转速度

def get_right_hand_action(fingers):
    if fingers == [1, 1, 1, 1, 1]:
        return 'Stop'
    elif fingers == [0, 1, 0, 0, 0]:
        return 'Up'
    elif fingers == [0, 1, 1, 0, 0]:
        return 'Down'
    elif fingers == [0, 0, 0, 0, 1]:
        return 'Left'
    elif fingers == [1, 0, 0, 0, 0]:
        return 'Right'
    elif fingers == [0, 0, 0, 0, 0]:
        return 'Forward'
    elif fingers == [1, 0, 0, 0, 1]:
        return 'Backward'
    else:
        return 'Unknown'

def get_left_hand_action(fingers):
    if fingers == [1, 0, 0, 0, 0]:
        return 'Rotate_Right'
    elif fingers == [0, 0, 0, 0, 1]:
        return 'Rotate_Left'
    elif fingers == [1, 0, 0, 0, 1]:
        return 'Backward'
    elif fingers == [0, 0, 0, 0, 0]:
        return 'Forward'
    elif fingers == [1, 1, 1, 1, 1]:
        return 'Stop'
    elif fingers == [0, 1, 0, 0, 0]:
        return 'Up'
    elif fingers == [0, 1, 1, 0, 0]:
        return 'Down'
    else:
        return 'Unknown'

def handle_gesture(fingers):
    global lr, fb, ud, yaw  # 使用全局变量
    # 初始化速度变量
    lr, fb, ud, yaw = 0, 0, 0, 0

    action = get_right_hand_action(fingers)

    # 根据手势执行操作
    if action == "Stop":
        lr, fb, ud, yaw = 0, 0, 0, 0
        tello.send_rc_control(lr, fb, ud, yaw)
        print("Drone will stop")
    elif action == "Up":
        ud = speed  # 向上上升
        print("Drone will move up")
    elif action == "Down":
        ud = -speed  # 向下下降
        print("Drone will move down")
    elif action == "Left":
        lr = -speed  # 向左移动
        print("Drone will move left")
    elif action == "Right":
        lr = speed  # 向右移动
        print("Drone will move right")
    elif action == "Forward":
        fb = speed  # 向前移动
        print("Drone will move forward")
    elif action == "Backward":
        fb = -speed  # 向后移动
        print("Drone will move backward")
    else:
        print("Unknown gesture")
        # 无法识别的手势时，停止
        lr, fb, ud, yaw = 0, 0, 0, 0
    return action

def handle_double_hand_gesture(left_fingers, right_fingers):
    global lr, fb, ud, yaw  # 使用全局变量
    # 初始化速度变量
    lr, fb, ud, yaw = 0, 0, 0, 0

    right_action = get_right_hand_action(right_fingers)
    left_action = get_left_hand_action(left_fingers)

    action = f"Right: {right_action}, Left: {left_action}"

    # 优先处理右手势
    if right_action == 'Stop':
        lr, fb, ud, yaw = 0, 0, 0, 0
    else:
        if right_action == 'Up':
            ud = speed
        elif right_action == 'Down':
            ud = -speed
        elif right_action == 'Left':
            lr = -speed
        elif right_action == 'Right':
            lr = speed
        elif right_action == 'Forward':
            fb = speed
        elif right_action == 'Backward':
            fb = -speed

    # 根据左手势执行操作
    # 冲突检测：左手和右手的命令冲突时忽略左手命令
    conflicting_actions = {
        'Up': 'Down',
        'Down': 'Up',
        'Forward': 'Backward',
        'Backward': 'Forward'
    }

    if left_action == 'Stop':
        lr, fb, ud, yaw = 0, 0, 0, 0
    elif left_action in ['Rotate_Right', 'Rotate_Left']:
        # 回转操作始终执行
        if left_action == 'Rotate_Right':
            yaw = yaw_speed  # 旋转时针方向
            print("Drone will rotate around you to the right")
        elif left_action == 'Rotate_Left':
            yaw = -yaw_speed  # 旋转反时针方向
            print("Drone will rotate around you to the left")
    elif left_action == right_action and right_action in ['Up', 'Down', 'Forward', 'Backward']:
        # 相同命令时，提高速度
        if right_action in ['Up', 'Down']:
            ud *= 1.5
        elif right_action in ['Forward', 'Backward']:
            fb *= 1.5
    elif left_action in conflicting_actions and conflicting_actions[left_action] == right_action:
        # 命令冲突时，忽略左手命令
        print(f"Same commands detected. Ignoring left hand command '{left_action}'.")
    else:
        # 其他情况下左手命令进一步处理 (根据需要实现)
        pass

    print(f"Double hand gesture detected: {action}")
    return action

try:
    while True:
        # 从 Tello 无人机摄像头获取帧
        frame_read = tello.get_frame_read()
        frame = frame_read.frame

        # 调整帧大小
        frame = cv2.resize(frame, (640, 480))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 手部检测
        hands, frame = detectorHand.findHands(frame)
        if hands:
            if len(hands) == 1:
                # 单手控制
                hand = hands[0]
                fingers = detectorHand.fingersUp(hand)
                
                # 输出手指状态
                print(f"Fingers: {fingers}")

                # 执行手势控制
                action = handle_gesture(fingers)
                
                # 发送控制命令到无人机
                tello.send_rc_control(int(lr), int(fb), int(ud), int(yaw))
                
                # 将手势信息显示在屏幕上
                cv2.putText(frame, action, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            elif len(hands) == 2:
                # 双手控制
                # 区分左手和右手
                if hands[0]['type'] == 'Left':
                    left_hand = hands[0]
                    right_hand = hands[1]
                else:
                    left_hand = hands[1]
                    right_hand = hands[0]

                left_fingers = detectorHand.fingersUp(left_hand)
                right_fingers = detectorHand.fingersUp(right_hand)

                # 输出手指状态
                print(f"Left Fingers: {left_fingers}")
                print(f"Right Fingers: {right_fingers}")

                # 执行双手手势控制
                action = handle_double_hand_gesture(left_fingers, right_fingers)
                
                # 发送控制命令到无人机
                tello.send_rc_control(int(lr), int(fb), int(ud), int(yaw))
                
                # 将手势信息显示在屏幕上
                cv2.putText(frame, action, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        else:
            # 当未检测到手时初始化速度变量
            lr, fb, ud, yaw = 0, 0, 0, 0
            action = "Stop"
            print("No hands detected. Drone will stop.")
            tello.send_rc_control(lr, fb, ud, yaw)
            # 将手势信息显示在屏幕上
            cv2.putText(frame, action, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # 显示帧
        cv2.imshow('Tello Drone', frame)
        
        # 按下 't' 键起飞，按下其他键降落并退出程序
        key = cv2.waitKey(1)
        if key == ord('t'):
            tello.takeoff()
        elif key != -1:
            tello.land()
            break
finally:
    # tello.land()
    cv2.destroyAllWindows()
