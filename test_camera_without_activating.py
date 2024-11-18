import cv2
from cvzone.HandTrackingModule import HandDetector
import time

# 핸드 탐지기 초기화
detectorHand = HandDetector(maxHands=1, detectionCon=0.9)  # 손 인식 신뢰도 증가

# FPS 조절을 위한 시간 변수 초기화
prev_time = 0
fps_limit = 120  # 원하는 FPS 설정

# 속도 변수 초기화
lr, fb, ud, yaw = 0, 0, 0, 0
speed = 30  # 드론 움직임 속도 설정

def handle_gesture(fingers):
    global lr, fb, ud, yaw  # 전역 변수 사용 선언
    # 속도 변수 초기화
    lr, fb, ud, yaw = 0, 0, 0, 0

    # 손 제스처에 따른 작업 수행
    if fingers == [1, 1, 1, 1, 1]:
        action = "Stop"
        print("Drone will stop")
        # 모든 속도를 0으로 유지
    elif fingers == [0, 1, 0, 0, 0]:
        action = "Up"
        ud = speed  # 위로 상승
        print("Drone will move up")
    elif fingers == [0, 1, 1, 0, 0]:
        action = "Down"
        ud = -speed  # 아래로 하강
        print("Drone will move down")
    elif fingers == [0, 0, 0, 0, 1]:
        action = "Left"
        lr = -speed  # 왼쪽으로 이동
        print("Drone will move left")
    elif fingers == [1, 0, 0, 0, 0]:
        action = "Right"
        lr = speed  # 오른쪽으로 이동
        print("Drone will move right")
    elif fingers == [0, 0, 0, 0, 0]:
        action = "Forward"
        fb = speed  # 앞으로 이동
        print("Drone will move forward")
    elif fingers == [1, 0, 0, 0, 1]:
        action = "Backward"
        fb = -speed  # 뒤로 이동
        print("Drone will move backward")
    else:
        action = "Unknown"
        print("Unknown gesture")
        # 알 수 없는 제스처일 경우 정지
    return action

try:
    # 웹캠 비디오 캡처 객체 생성
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:
        # 현재 시간 측정
        curr_time = time.time()
        elapsed_time = curr_time - prev_time
        if elapsed_time < 1.0 / fps_limit:
            time.sleep(0.01)  # 일정한 대기 시간 추가
            continue
        prev_time = curr_time

        # 웹캠에서 프레임 가져오기
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame from webcam")
            break

        # 프레임 크기 조정
        frame = cv2.resize(frame, (1280, 720))
        
        # 손 인식
        hands, frame = detectorHand.findHands(frame)
        if hands:
            hand = hands[0]
            fingers = detectorHand.fingersUp(hand)
            
            # 손가락 상태 출력
            print(f"Fingers: {fingers}")

            # 제스처 제어 실행
            action = handle_gesture(fingers)
            
            # 제스처 정보 화면에 출력
            cv2.putText(frame, f'Gesture: {action}', (10, 60), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        else:
            # 손이 인식되지 않을 때 속도 변수 초기화
            lr, fb, ud, yaw = 0, 0, 0, 0
            action = "Stop"
            print("No hands detected. Drone will stop.")
            # 제스처 정보 화면에 출력
            cv2.putText(frame, 'Gesture: Stop', (10, 60), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        # 프레임 출력
        cv2.imshow('Webcam', frame)
        
        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # 캡처 객체 및 OpenCV 창 닫기
    cap.release()
    cv2.destroyAllWindows()
