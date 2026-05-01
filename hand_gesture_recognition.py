import cv2
import mediapipe as mp
import numpy as np
import time
import imageio.v2 as iio

class GifPlayer:
    def __init__(self, gif_path):
        """初始化 GIF 播放器"""
        try:
            self.frames = iio.mimread(gif_path)
            print(f"成功加载 GIF，共 {len(self.frames)} 帧")
        except Exception as e:
            print(f"GIF 加载失败: {e}")
            self.frames = self._create_test_frames()
        
        self.num_frames = len(self.frames)
        self.idx = 0
        self.active = False
    
    def _create_test_frames(self):
        """如果没有 GIF，创建测试用的彩色动画"""
        frames = []
        for i in range(30):
            frame = np.zeros((100, 100, 4), dtype=np.uint8)
            color = (i * 8 % 255, 255 - i * 8 % 255, 128, 200)
            cv2.circle(frame, (50, 50), 40, color, -1)
            cv2.putText(frame, "GIF", (30, 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255, 255), 2)
            frames.append(frame)
        print("使用测试动画")
        return frames
    
    def update(self):
        """更新当前帧，返回 BGR 格式的图像"""
        if self.active and self.num_frames > 0:
            frame = self.frames[self.idx]
            self.idx = (self.idx + 1) % self.num_frames
            
            if frame.shape[2] == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            elif frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGRA)
            
            return frame
        return None
    
    def start(self):
        self.active = True
        self.idx = 0
    
    def stop(self):
        self.active = False

def overlay_gif_alpha(frame, gif_frame, x, y, size=(120, 120)):
    """将 GIF 帧叠加到视频帧上（支持透明通道）"""
    if gif_frame is None:
        return frame
    
    gif_resized = cv2.resize(gif_frame, size)
    h, w = gif_resized.shape[:2]
    
    if y + h > frame.shape[0] or x + w > frame.shape[1]:
        return frame
    
    roi = frame[y:y+h, x:x+w]
    
    if gif_resized.shape[2] == 4:
        gif_bgr = gif_resized[:, :, :3]
        gif_alpha = gif_resized[:, :, 3] / 255.0
        
        for c in range(3):
            roi[:, :, c] = (1 - gif_alpha) * roi[:, :, c] + gif_alpha * gif_bgr[:, :, c]
        
        frame[y:y+h, x:x+w] = roi
    else:
        frame[y:y+h, x:x+w] = gif_resized
    
    return frame

# 初始化 MediaPipe
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

face_detection = mp_face.FaceDetection(
    model_selection=0,
    min_detection_confidence=0.5
)

def is_palm_facing_camera(hand_landmarks):
    """判断掌心是否朝向镜头"""
    thumb_tip = hand_landmarks.landmark[4].x
    pinky_tip = hand_landmarks.landmark[20].x
    return abs(thumb_tip - pinky_tip) > 0.1

def are_fingers_curled(hand_landmarks, threshold=0.025):
    """检测四指是否微曲"""
    finger_pairs = [(8,5), (12,9), (16,13), (20,17)]
    curled_count = 0
    for tip_id, base_id in finger_pairs:
        diff_y = hand_landmarks.landmark[tip_id].y - hand_landmarks.landmark[base_id].y
        if diff_y < threshold:
            curled_count += 1
    return curled_count == 4

def is_palm_up_and_curled(hand_landmarks, hand_type):
    """
    判断是否为「手心向上 + 手指微曲 + 中指高于手腕」手势
    """
    # 条件1：掌心朝向摄像头
    #if not is_palm_facing_camera(hand_landmarks):
        #return False
    
    # 条件2：手指微曲
    if not are_fingers_curled(hand_landmarks):
        return False
    
    # 条件3：中指（ID 12）的 Y 坐标小于手腕（ID 0）的 Y 坐标
    # 因为图像坐标系中 Y 轴向下，所以 smaller Y = 更高位置
    middle_tip_y = hand_landmarks.landmark[10].y
    wrist_y = hand_landmarks.landmark[0].y
    
    if middle_tip_y <= wrist_y:
        return False  # 中指没有高于手腕
    
    return True

def count_fingers_v2(hand_landmarks, hand_type, is_palm):
    """计算伸出了几根手指，并检测中指和食指是否靠拢"""
    fingers = []
    
    # 大拇指判断
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]

    if hand_type == 'Right':
        if is_palm:
            fingers.append(1 if thumb_tip.x < thumb_ip.x else 0)
        else:
            fingers.append(1 if thumb_tip.x > thumb_ip.x else 0)
    else:
        if is_palm:
            fingers.append(1 if thumb_tip.x > thumb_ip.x else 0)
        else:
            fingers.append(1 if thumb_tip.x < thumb_ip.x else 0)

    # 检测中指和食指是否靠拢（触发贴图手势）
    index_x = hand_landmarks.landmark[8].x
    middle_x = hand_landmarks.landmark[12].x
    index_y = hand_landmarks.landmark[8].y
    middle_pip_y = hand_landmarks.landmark[10].y
    
    # 如果中指和食指靠拢且食指伸直
    if abs(middle_x - index_x) < 0.02 and index_y < middle_pip_y:
        return 6  # 触发贴图
    
    # 其他四指判断
    tip_ids = [8, 12, 16, 20]
    for tip_id in tip_ids:
        tip_y = hand_landmarks.landmark[tip_id].y
        pip_y = hand_landmarks.landmark[tip_id - 2].y
        
        if tip_y < pip_y:
            fingers.append(1)
        else:
            fingers.append(0)
    
    return sum(fingers)

def get_gesture_name(finger_count):
    """根据手指数量返回手势名称"""
    gestures = {
        0: "Fist",
        1: "One",
        2: "Victory",
        3: "Three",
        4: "Four",
        5: "Open Palm",
        6: "Trigger Face Mask!"
    }
    return gestures.get(finger_count, f"{finger_count} fingers")

def overlay_image_alpha(img, img_overlay, x, y, overlay_size=None):
    """在指定位置叠加透明图像"""
    if overlay_size is not None:
        img_overlay = cv2.resize(img_overlay, overlay_size)
    
    h, w = img_overlay.shape[:2]
    
    if y + h > img.shape[0] or x + w > img.shape[1]:
        return img
    
    if img_overlay.shape[2] == 4:
        alpha = img_overlay[:, :, 3] / 255.0
        for c in range(0, 3):
            img[y:y+h, x:x+w, c] = (1 - alpha) * img[y:y+h, x:x+w, c] + alpha * img_overlay[:, :, c]
    else:
        img[y:y+h, x:x+w] = img_overlay
    
    return img

def create_test_sticker():
    """创建一个测试用的贴图"""
    sticker = np.zeros((200, 200, 4), dtype=np.uint8)
    cv2.circle(sticker, (100, 100), 80, (0, 255, 255, 255), -1)
    cv2.circle(sticker, (60, 70), 15, (0, 0, 0, 255), -1)
    cv2.circle(sticker, (140, 70), 15, (0, 0, 0, 255), -1)
    cv2.ellipse(sticker, (100, 130), (40, 25), 0, 0, 180, (0, 0, 0, 255), -1)
    return sticker

# 加载贴图
try:
    face_sticker = cv2.imread('muliao_kusho.jpg', cv2.IMREAD_UNCHANGED)
    if face_sticker is None:
        raise FileNotFoundError
    print("Loaded custom sticker image")
except:
    print("Using default smiley sticker")
    face_sticker = create_test_sticker()

# 初始化 GIF 播放器（放在循环外，只初始化一次）
gif_player = GifPlayer('rasengan.gif')

# 打开摄像头
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("\nCamera started!")
print("Controls:")
print("  'q' - Quit")
print("  's' - Screenshot")
print("\nGesture detection running...")
print("  🤏 Pinch middle and index fingers together - Face sticker")
print("  🖐️ Palm up with curled fingers - GIF above hand\n")

frame_count = 0
fps = 0
prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    
    frame = cv2.flip(frame, 1)
    
    frame_count += 1
    current_time = time.time()
    if current_time - prev_time >= 1.0:
        fps = frame_count
        frame_count = 0
        prev_time = current_time
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hand_result = hands.process(frame_rgb)
    
    # 默认值
    gesture_text = "No hand detected"
    finger_count = 0
    apply_sticker = False
    is_palm_up = False  # 新增：标记手心向上手势
    
    if hand_result.multi_hand_landmarks:
        for hand_idx, hand_landmarks in enumerate(hand_result.multi_hand_landmarks):
            hand_type = hand_result.multi_handedness[hand_idx].classification[0].label
            
            # 获取掌心朝向
            is_palm = is_palm_facing_camera(hand_landmarks)
            facing = "palm" if is_palm else "back"  # ✅ 修正 facing 变量
            
            # 计算手指数量（返回 0-6）
            finger_count = count_fingers_v2(hand_landmarks, hand_type, is_palm)
            gesture_text = get_gesture_name(finger_count)
            
            # 检查是否触发贴图（finger_count == 6）
            if finger_count == 6:
                apply_sticker = True
            
            # 检测手心向上 + 手指微曲（手势2）
            if is_palm_up_and_curled(hand_landmarks, hand_type):
                is_palm_up = True
                if not gif_player.active:
                    gif_player.start()
            else:
                if gif_player.active:
                    gif_player.stop()
            
            # 显示手部信息
            cv2.putText(frame, f"{hand_type} ({facing})", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # 绘制手部关键点
            mp_draw.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2),
                mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2)
            )
    
    # 绘制 GIF（手势2触发）
    if gif_player.active:
        gif_frame = gif_player.update()
        if gif_frame is not None and hand_result.multi_hand_landmarks:
            # 使用第一只手的坐标
            hand_landmarks = hand_result.multi_hand_landmarks[0]
            wrist = hand_landmarks.landmark[0]
            h, w, _ = frame.shape
            center_x = int(wrist.x * w)
            center_y = int(wrist.y * h) - 100
            
            x = max(0, center_x - 60)
            y = max(0, center_y - 60)
            frame = overlay_gif_alpha(frame, gif_frame, x, y, (120, 120))
    
    # 人脸贴图（手势1触发）
    if apply_sticker:
        face_result = face_detection.process(frame_rgb)
        
        if face_result.detections:
            for detection in face_result.detections:
                bboxC = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                
                x = int(bboxC.xmin * w)
                y = int(bboxC.ymin * h)
                box_w = int(bboxC.width * w)
                box_h = int(bboxC.height * h)
                
                sticker_w = box_w
                sticker_h = box_h
                sticker_x = x + (box_w - sticker_w) // 2
                sticker_y = y - sticker_h // 4
                
                sticker_x = max(0, sticker_x)
                sticker_y = max(0, sticker_y)
                
                sticker_resized = cv2.resize(face_sticker, (sticker_w, sticker_h))
                
                if sticker_y + sticker_h <= h and sticker_x + sticker_w <= w:
                    overlay_image_alpha(frame, sticker_resized, sticker_x, sticker_y)
    
    # 显示信息栏
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], 90), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
    
    cv2.putText(frame, f"FPS: {fps}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Gesture: {gesture_text} ({finger_count} fingers)", 
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # 状态提示
    if apply_sticker:
        cv2.putText(frame, "FACE STICKER ACTIVE!", 
                    (frame.shape[1] - 300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    elif is_palm_up:
        cv2.putText(frame, "GIF ACTIVE! (Palm up + curled fingers)", 
                    (frame.shape[1] - 380, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "Pinch fingers -> Face sticker | Palm up + curled -> GIF", 
                    (frame.shape[1] - 450, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
    
    cv2.putText(frame, "Q:Quit  S:Save", 
                (frame.shape[1] - 150, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    cv2.imshow('Hand Gesture Detection + Face Sticker', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        cv2.imwrite(f"sticker_{timestamp}.jpg", frame)
        print(f"Screenshot saved: sticker_{timestamp}.jpg")

cap.release()
cv2.destroyAllWindows()
hands.close()
face_detection.close()
print("\nProgram ended!")