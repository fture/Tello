import cv2
from cvzone.HandTrackingModule import HandDetector
import time

detectorHand = HandDetector(maxHands=2, detectionCon=0.8)

prev_time = 0
fps_limit = 120

lr, fb, ud, yaw = 0, 0, 0, 0
speed = 30
yaw_speed = 30

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
    if fingers == [0, 0, 0, 0, 1]:
        return 'Rotate_Right'
    elif fingers == [1, 0, 0, 0, 0]:
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
    global lr, fb, ud, yaw
    lr, fb, ud, yaw = 0, 0, 0, 0

    action = get_right_hand_action(fingers)

    if action == "Stop":
        print("Drone will stop")
    elif action == "Up":
        ud = speed
        print("Drone will move up")
    elif action == "Down":
        ud = -speed
        print("Drone will move down")
    elif action == "Left":
        lr = -speed
        print("Drone will move left")
    elif action == "Right":
        lr = speed
        print("Drone will move right")
    elif action == "Forward":
        fb = speed
        print("Drone will move forward")
    elif action == "Backward":
        fb = -speed
        print("Drone will move backward")
    else:
        print("Unknown gesture")
    return action

def handle_double_hand_gesture(left_fingers, right_fingers):
    global lr, fb, ud, yaw
    lr, fb, ud, yaw = 0, 0, 0, 0

    right_action = get_right_hand_action(right_fingers)
    left_action = get_left_hand_action(left_fingers)

    action = f"Right: {right_action}, Left: {left_action}"

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

    conflicting_actions = {
        'Up': 'Down',
        'Down': 'Up',
        'Forward': 'Backward',
        'Backward': 'Forward'
    }

    if left_action == 'Stop':
        lr, fb, ud, yaw = 0, 0, 0, 0
    elif left_action in ['Rotate_Right', 'Rotate_Left']:
        if left_action == 'Rotate_Right':
            yaw = yaw_speed
            print("Drone will rotate around you to the right")
        elif left_action == 'Rotate_Left':
            yaw = -yaw_speed
            print("Drone will rotate around you to the left")
    elif left_action == right_action and right_action in ['Up', 'Down', 'Forward', 'Backward']:
        if right_action in ['Up', 'Down']:
            ud *= 1.5
        elif right_action in ['Forward', 'Backward']:
            fb *= 1.5
    elif left_action in conflicting_actions and conflicting_actions[left_action] == right_action:
        print(f"Conflicting commands detected. Ignoring left hand command '{left_action}'.")
    else:
        pass

    print(f"Double hand gesture detected: {action}")
    return action

try:
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while True:

        curr_time = time.time()
        elapsed_time = curr_time - prev_time
        if elapsed_time < 1.0 / fps_limit:
            time.sleep(0.01)
            continue
        prev_time = curr_time

        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame from webcam")
            break

        frame = cv2.resize(frame, (480, 320))
        
        hands, frame = detectorHand.findHands(frame)
        if hands:
            if len(hands) == 1:
                hand = hands[0]
                fingers = detectorHand.fingersUp(hand)
                
                print(f"Fingers: {fingers}")

                action = handle_gesture(fingers)
                
                cv2.putText(frame, f'Gesture: {action}', (10, 60), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
            elif len(hands) == 2:
                if hands[0]['type'] == 'Left':
                    left_hand = hands[0]
                    right_hand = hands[1]
                else:
                    left_hand = hands[1]
                    right_hand = hands[0]

                left_fingers = detectorHand.fingersUp(left_hand)
                right_fingers = detectorHand.fingersUp(right_hand)

                print(f"Left Fingers: {left_fingers}")
                print(f"Right Fingers: {right_fingers}")

                action = handle_double_hand_gesture(left_fingers, right_fingers)
                
                cv2.putText(frame, f'Double Gesture: {action}', (10, 60), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        else:
            lr, fb, ud, yaw = 0, 0, 0, 0
            action = "Stop"
            print("No hands detected. Drone will stop.")
            cv2.putText(frame, 'Gesture: Stop', (10, 60), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        cv2.imshow('Webcam', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
