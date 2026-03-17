# utils.py

from datetime import datetime

from config import f_w, f_s, f_l, W_REAL, S_REAL, L_REAL


def select_f_and_size(aspect: float):
    """bbox aspect ratio로 거리 추정에 사용할 focal length / real size / label 선택"""
    if aspect <= 0.80:  # 정면
        return f_w, W_REAL, "W"
    elif aspect <= 1.08:  # 45도 부근
        return f_s, S_REAL, "S"
    else:  # 측면
        return f_l, L_REAL, "L"


def is_similar_object(new_obj, existing_obj, pos_thresh=150, theta_thresh=10):
    dx = abs(new_obj["x"] - existing_obj["x"])
    dy = abs(new_obj["y"] - existing_obj["y"])
    dtheta = abs(new_obj["theta"] - existing_obj["theta"])
    return dx < pos_thresh and dy < pos_thresh and dtheta < theta_thresh


def interpolate_object(before, after):
    w1 = 1 / (abs(before["dx"]) + 1e-6)
    w2 = 1 / (abs(after["dx"]) + 1e-6)
    total = w1 + w2

    def w_avg(key):
        return (before[key] * w1 + after[key] * w2) / total

    return {
        "distance": w_avg("distance"),
        "theta": w_avg("theta"),
        "x": w_avg("x"),
        "y": w_avg("y"),
        "dx": w_avg("dx"),
        "confidence": w_avg("confidence"),
        "label": before.get("label", ""),
        "aspect": before.get("aspect", 0.0),
        "timestamp": after.get(
            "timestamp", datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        ),
    }


def print_full_matrix(full_matrix):
    print("------ [Full Matrix State] ------")
    for idx, obj in enumerate(full_matrix):
        print(
            f"ID {idx}: "
            f"x={obj['x']:.1f}, y={obj['y']:.1f}, "
            f"θ={obj['theta']:.1f}, z={obj['distance']:.1f}, "
            f"dx={obj['dx']:.1f}, t={obj['timestamp']}"
        )
    print("---------------------------------")


def print_candidate_matrix(candidate_buffer):
    print("------ [Candidate State] ------")
    for idx, obj in enumerate(candidate_buffer):
        print(
            f"ID {idx}: "
            f"x={obj['x']:.1f}, y={obj['y']:.1f}, "
            f"θ={obj['theta']:.1f}, z={obj['distance']:.1f}, "
            f"dx={obj['dx']:.1f}, t={obj['timestamp']}"
        )
    print("---------------------------------")
