# config.py

from pathlib import Path

# 프로젝트 루트 기준 경로
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
MODELS_DIR = ASSETS_DIR / "models"
CALIB_DIR = ASSETS_DIR / "calibration"

MODEL_PATH = str(MODELS_DIR / "best_320_dowan.onnx")
CALIB_PATH = str(CALIB_DIR / "camera_calibration_0519.npz")

# YOLO / frame
IMG_SIZE = 320
FRAME_WIDTH = 1280

# 객체 실제 크기(mm)
H_REAL = 303
W_REAL = 240
L_REAL = 320
S_REAL = 400

# 초점거리(px)
# 기존 단일 코드 호환을 위해 소문자 이름 유지
f_w = 482
f_l = 451
f_s = 372

# 혹시 다른 파일에서 대문자 버전을 쓸 수도 있으니 alias도 같이 둠
F_W = f_w
F_L = f_l
F_S = f_s

# detection / smoothing
MAX_DX = 200
BASE_DX = 200

# gimbal
YAW_SPEED = 40
ANGLES = 80

# motion
DURATION = 0.3
RATE = 4.0
REPEL_THRESH = 0.6
ADJ_RADIUS = 0.7

MAX_WEIGHT = 5.0
MIN_WEIGHT = 2.0

# communication
MAX_CONFIRM_THRESHOLD = 2
MAX_RESET_TIMEOUT = 10
UDP_IP = "255.255.255.255"
UDP_PORT = 5005
