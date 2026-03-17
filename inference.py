# inference.py

import time
from datetime import datetime

from ultralytics import YOLO

from config import IMG_SIZE, FRAME_WIDTH, MODEL_PATH
from utils import select_f_and_size
from estimation import estimate_local_coordinates


def create_model(model_path=MODEL_PATH):
    """
    YOLO ONNX 모델 로드
    """
    return YOLO(model_path)


def run_yolo_loop(state, sync, model):
    prev_frame = None

    while True:
        with sync["inference_lock"]:
            frame = state["shared_frame"]
            theta = state["now_theta"]

        if frame is None:
            time.sleep(0.05)
            continue

        # 이전 프레임과 동일 객체 참조면 건너뜀
        if frame is prev_frame:
            time.sleep(0.03)
            continue

        prev_frame = frame
        frame_for_infer = frame.copy()

        results = model(frame_for_infer, imgsz=IMG_SIZE, verbose=False)
        boxes = results[0].boxes

        local_results = []
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]

        pred_sorted = sorted(
            boxes,
            key=lambda det: abs(
                ((det.xyxy[0][0] + det.xyxy[0][2]) / 2) - FRAME_WIDTH / 2
            ),
        )

        for box in pred_sorted:
            conf = float(box.conf[0].cpu().numpy())
            if conf < 0.15:
                continue

            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

            bbox_width = x2 - x1
            bbox_height = y2 - y1
            cx = (x1 + x2) / 2
            dx = cx - (FRAME_WIDTH / 2)

            if bbox_width <= 0:
                continue

            aspect = bbox_width / (bbox_height + 1e-6)
            f_sel, real_size, label = select_f_and_size(aspect)

            distance = (f_sel * real_size) / bbox_width
            x, y, local_theta = estimate_local_coordinates(
                distance=distance,
                dx_px=dx,
                yaw_angle=theta,
                focal_length=f_sel,
            )

            obj = {
                "x": x,
                "y": y,
                "distance": distance,
                "aspect": aspect,
                "label": label,
                "theta": local_theta,
                "dx": dx,
                "confidence": conf,
                "timestamp": timestamp,
            }
            local_results.append(obj)

        with sync["inference_lock"]:
            state["results_list"] = local_results
            state["shared_yolo_matrix"] = local_results

        time.sleep(0.07)
