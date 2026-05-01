

---

## 🇨🇳 中文版 `README.md`

```markdown`
# 手勢辨識系統 - 人臉貼圖 & GIF 動畫

這是一個基於 **MediaPipe** 和 **OpenCV** 的即時手勢辨識應用程式。透過網路攝影機，你可以用手勢觸發兩種特效：

- 🤏 **捏合中指與食指** → 在人臉上貼圖
- 🖐️ **手心向上 + 手指微曲 + 中指高於手腕** → 在手部上方播放 GIF 動畫（例如：螺旋丸）

## 📸 功能示範

| 手勢 | 效果 |
|------|------|
| 食指 + 中指捏合（距離 < 0.02） | 人臉貼圖 |
| 手心向上 + 四指微曲 + 中指高於手腕 | 播放 GIF 動畫 |

## 🛠️ 系統需求

- Python 3.8 ~ 3.10
- 網路攝影機
- Windows / macOS / Linux

## 📦 安裝與執行

### 1. 下載專案

```bash
git clone https://github.com/你的帳號/Hand-Gesture-Recognition.git
cd Hand-Gesture-Recognition
```

### 2. 安裝依賴套件

建議使用虛擬環境：

```bash
# 建立虛擬環境（可選）
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安裝所有套件
pip install -r requirements.txt
```

### 3. 執行程式

```bash
python hand_gesture_recognition.py
```

## 🎮 操作方式

| 按鍵 | 功能 |
|------|------|
| `q` | 退出程式 |
| `s` | 儲存當前畫面（包含特效） |

## 📁 專案結構

```
Hand-Gesture-Recognition/
├── hand_gesture_recognition.py   # 主程式
├── muliao_kusho.jpg              # 人臉貼圖（可更換）
├── rasengan.gif                  # GIF 動畫（可更換）
├── requirements.txt              # 套件依賴清單
└── README.md                     # 專案說明
```

## ⚙️ 手勢偵測原理

### 捏合手勢（人臉貼圖）
- 偵測中指（ID 12）與食指（ID 8）的 X 座標距離
- 距離 < 0.02 即觸發

### 手心向上 + 手指微曲（GIF 動畫）
- 掌心朝向攝影機（拇指與小指的 X 座標差 > 0.1）
- 四指微曲（指尖與指根的 Y 座標差 < 0.025）
- 中指 Y 座標 < 手腕 Y 座標（表示手抬高）

## 📝 依賴套件版本

```
opencv-python==4.9.0.80
mediapipe==0.10.14
numpy==1.24.3
imageio==2.31.6
imageio-ffmpeg==0.4.9
```

## ⚠️ 注意事項

- 確保光線充足，背景單純，以提高偵測準確度
- 手部距離攝影機約 30~50 公分效果最佳
- 如果偵測不準，可調整程式中的靈敏度參數（如 `0.02`、`0.025` 等）

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

---

## 🇬🇧 英文版 `README.en.md`
```
```markdown```
```
# Hand Gesture Recognition - Face Sticker & GIF Animation

A real-time hand gesture recognition application based on **MediaPipe** and **OpenCV**. Use your webcam to trigger two visual effects with hand gestures:

- 🤏 **Pinch middle & index fingers** → Apply sticker on detected face
- 🖐️ **Palm up + curled fingers + middle finger above wrist** → Play GIF animation above hand (e.g., Rasengan)

## 📸 Demo

| Gesture | Effect |
|---------|--------|
| Pinched middle & index fingers (distance < 0.02) | Face sticker |
| Palm up + 4 curled fingers + middle finger above wrist | GIF animation |

## 🛠️ Requirements

- Python 3.8 ~ 3.10
- Webcam
- Windows / macOS / Linux

## 📦 Installation & Usage

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Hand-Gesture-Recognition.git
cd Hand-Gesture-Recognition
```

### 2. Install dependencies

Using a virtual environment is recommended:

```bash
# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install all packages
pip install -r requirements.txt
```

### 3. Run the program

```bash
python hand_gesture_recognition.py
```

## 🎮 Controls

| Key | Function |
|-----|----------|
| `q` | Quit program |
| `s` | Save screenshot (with effects) |

## 📁 Project Structure

```
Hand-Gesture-Recognition/
├── hand_gesture_recognition.py   # Main script
├── muliao_kusho.jpg              # Face sticker (replaceable)
├── rasengan.gif                  # GIF animation (replaceable)
├── requirements.txt              # Dependencies list
└── README.md                     # Documentation
```

## ⚙️ Gesture Detection Logic

### Pinch Gesture (Face Sticker)
- Detects X-coordinate distance between middle finger (ID 12) and index finger (ID 8)
- Trigger when distance < 0.02

### Palm Up + Curled Fingers (GIF Animation)
- Palm facing camera (thumb & pinky X-coordinate difference > 0.1)
- Four fingers curled (Y-coordinate difference between fingertip & knuckle < 0.025)
- Middle finger Y-coordinate < wrist Y-coordinate (hand raised)

## 📝 Dependency Versions

```
opencv-python==4.9.0.80
mediapipe==0.10.14
numpy==1.24.3
imageio==2.31.6
imageio-ffmpeg==0.4.9
```

## ⚠️ Notes

- Ensure good lighting and a plain background for better detection accuracy
- Keep hand 30~50 cm away from the camera for optimal results
- If detection is inaccurate, adjust sensitivity parameters in the code (e.g., `0.02`, `0.025`)

## 🤝 Contributing

Issues and Pull Requests are welcome!

