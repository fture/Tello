from djitellopy import Tello 
import cv2
from cvzone.HandTrackingModule import HandDetector
import time

# 创建 Tello 对象并连接
tello = Tello()
tello.connect()

# 检查电池电量
print(f'Battery: {tello.get_battery()}%')

# 开启视频流
tello.streamon()

# 等待摄像头连接
time.sleep(2)


# 初始化手部检测器
detectorHand = HandDetector(maxHands=1, detectionCon=0.9)  # 提高手势检测的可信度

# 初始化速度变量
lr, fb, ud, yaw = 0, 0, 0, 0
speed = 30  # 设置无人机移动速度

def handle_gesture(fingers):
    global lr, fb, ud, yaw
    # 重置速度变量
    lr, fb, ud, yaw = 0, 0, 0, 0

    # 根据手势执行动作
    if fingers == [1, 1, 1, 1, 1]:
        action = "Stop"
        print("Drone will stop")
        # 保持所有速度为 0
    elif fingers == [0, 1, 0, 0, 0]:
        action = "Up"
        ud = speed  # 向上移动
        print("Drone will move up")
    elif fingers == [0, 1, 1, 0, 0]:
        action = "Down"
        ud = -speed  # 向下移动
        print("Drone will move down")
    elif fingers == [0, 0, 0, 0, 1]:
        action = "Left"
        lr = -speed  # 向左移动
        print("Drone will move left")
    elif fingers == [1, 0, 0, 0, 0]:
        action = "Right"
        lr = speed  # 向右移动
        print("Drone will move right")
    elif fingers == [0, 0, 0, 0, 0]:
        action = "Forward"
        fb = speed  # 向前移动
        print("Drone will move forward")
    elif fingers == [1, 0, 0, 0, 1]:
        action = "Backward"
        fb = -speed  # 向后移动
        print("Drone will move backward")
    else:
        action = "Unknown"
        print("Unknown gesture")
        # 对于无法识别的手势，保持悬停
    return action

try:
    while True:
        # 从无人机摄像头获取帧
        frame = tello.get_frame_read().frame

        # 调整帧大小并转换颜色
        frame = cv2.resize(frame, (480, 320))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 检测手部
        hands, frame = detectorHand.findHands(frame)
        if hands:
            hand = hands[0]
            fingers = detectorHand.fingersUp(hand)
            
            # 输出手指状态
            print(f"Fingers: {fingers}")

            # 执行手势控制
            action = handle_gesture(fingers)
            
            # 将手势信息显示在屏幕上
            cv2.putText(frame, action, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            # 当未检测到手时重置速度变量
            lr, fb, ud, yaw = 0, 0, 0, 0
            action = "Stop"
            print("No hands detected. Drone will stop.")
            # 将手势信息显示在屏幕上
            cv2.putText(frame, action, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # 发送速度命令到无人机
        tello.send_rc_control(lr, fb, ud, yaw)

        # 显示帧
        cv2.imshow('Tello Camera', frame)
        
        # 按下 't' 键起飞，按下其他键降落并退出程序
        key = cv2.waitKey(1)
        if key == ord('t'):            
            tello.takeoff()
            # tello.send_rc_control(0, 0, 30, 0)
            # time.sleep(2)
            # tello.send_rc_control(0, 0, 0, 0)
        elif key != -1:
            tello.land()
            break
finally:
    # 停止无人机视频流并断开连接
    tello.streamoff()
    tello.end()
    # 关闭 OpenCV 窗口
    cv2.destroyAllWindows()
