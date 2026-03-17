# smoothing.py

import time
from datetime import datetime

from config import BASE_DX
from utils import (
    is_similar_object,
    interpolate_object,
    print_candidate_matrix,
    print_full_matrix,
)


def save_or_update_object(new_obj, state, sync):
    with sync["inference_lock"]:
        for obj in state["full_matrix"]:
            if is_similar_object(new_obj, obj):
                obj.update(new_obj)
                return
        state["full_matrix"].append(new_obj)


def smoothing_loop(state, sync):
    update_interval = 0.15

    while True:
        time.sleep(0.05)

        with sync["inference_lock"]:
            local_copy = state["shared_yolo_matrix"].copy()

        if not local_copy:
            continue

        for obj in local_copy:
            obj["timestamp"] = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]

        for obj in local_copy:
            dx = obj["dx"]
            abs_dx = abs(dx)
            curr_sign = 1 if dx > 0 else (-1 if dx < 0 else 0)

            if len(local_copy) >= 2:
                dxs = sorted([o["dx"] for o in local_copy])
                min_diff = min(
                    BASE_DX, min(abs(dxs[i + 1] - dxs[i]) for i in range(len(dxs) - 1))
                )
                print(f"[Min_diff 결정] {min_diff}")

                if abs_dx > (min_diff / 2):
                    continue
            else:
                if abs_dx >= BASE_DX:
                    continue

            prev_dx = state["prev_dx"]
            prev_sign = state["prev_sign"]

            if prev_dx is not None:
                if curr_sign == prev_sign and abs_dx > abs(prev_dx):
                    print("[필터] 같은 방향으로 멀어짐 → 제외")
                    state["prev_dx"] = dx
                    state["prev_sign"] = curr_sign
                    continue

            with sync["inference_lock"]:
                state["candidate_buffer"].append(obj)
                candidate_snapshot = state["candidate_buffer"].copy()

            print_candidate_matrix(candidate_snapshot)

            state["prev_dx"] = dx
            state["prev_sign"] = curr_sign

        with sync["inference_lock"]:
            candidate_snapshot = state["candidate_buffer"].copy()

        if len(candidate_snapshot) >= 2:
            for i in range(1, len(candidate_snapshot)):
                s1 = (
                    1
                    if candidate_snapshot[i - 1]["dx"] > 0
                    else (-1 if candidate_snapshot[i - 1]["dx"] < 0 else 0)
                )
                s2 = (
                    1
                    if candidate_snapshot[i]["dx"] > 0
                    else (-1 if candidate_snapshot[i]["dx"] < 0 else 0)
                )

                if s1 != s2:
                    obj_interp = interpolate_object(
                        candidate_snapshot[i - 1], candidate_snapshot[i]
                    )
                    save_or_update_object(obj_interp, state, sync)

                    with sync["inference_lock"]:
                        full_snapshot = state["full_matrix"].copy()
                        state["candidate_buffer"].clear()

                    print_full_matrix(full_snapshot)
                    break

        time.sleep(update_interval)
