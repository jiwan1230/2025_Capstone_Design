# control.py

import time
import numpy as np

from config import ADJ_RADIUS
from config import REPEL_THRESH
from config import ANGLES, YAW_SPEED, DURATION


class MecanumWheelController:
    def __init__(self, chassis):
        self.chassis = chassis
        self.RPM_PER_METER = 285
        self.MAX_RPM = 100
        self.MIN_RPM = 20

    def vector_to_mecanum_wheel_ratio(self, vx, vy):
        w1 = vy - vx
        w2 = vy + vx
        w3 = vy + vx
        w4 = vy - vx
        return np.array([w1, w2, w3, w4], dtype=float)

    def vector_to_mecanum_wheel_ratio_repel(self, vx, vy):
        w1 = vy + vx
        w2 = vy - vx
        w3 = vy - vx
        w4 = vy + vx
        return np.array([w1, w2, w3, w4], dtype=float)

    def calc_wheel_rpm(self, task_vector, magnitude, heading):
        vx, vy = task_vector

        if magnitude == 0:
            return np.array([0.0, 0.0, 0.0, 0.0])

        rpm = self.MIN_RPM + (self.MAX_RPM - self.MIN_RPM) * min(
            magnitude / 1000.0, 1.0
        )

        if heading:
            wheel_ratio = self.vector_to_mecanum_wheel_ratio(vx, vy)
            print("[Mecanum Wheel] 일반 Ratio")
        else:
            wheel_ratio = self.vector_to_mecanum_wheel_ratio_repel(vx, vy)
            print("[Mecanum Wheel] 후진 Ratio")

        return rpm * wheel_ratio

    def set_wheel_speed(self, wheel_rpm):
        clipped = [max(min(float(r), self.MAX_RPM), -self.MAX_RPM) for r in wheel_rpm]
        w1, w2, w3, w4 = clipped
        self.chassis.drive_wheels(w1, w2, w3, w4)

    def drive_vector(self, task_vector, magnitude, duration, heading):
        wheel_rpm = self.calc_wheel_rpm(task_vector, magnitude, heading)

        for _ in range(int(duration / 0.1)):
            self.set_wheel_speed(wheel_rpm)
            time.sleep(0.1)

        self.set_wheel_speed([0, 0, 0, 0])


def approach_with_mecanum(task_vector, magnitude, wheel_controller, duration, heading):
    if task_vector is None:
        print("[Approach] 안정 상태로 이동 생략")
        return

    vx, vy = task_vector
    print(f"[Debug] vx = {vx}, vy = {vy}")
    wheel_controller.drive_vector([vx, vy], magnitude, duration, heading)


def compute_task_vector_with_weighted_consensus(
    full_matrix,
    adj_radius=ADJ_RADIUS,
    repel_thresh=REPEL_THRESH,
):
    if not full_matrix:
        return None, 0.0, 1

    vectors = []
    heading = 1
    normalization = 1000.0  # mm -> m

    for obj in full_matrix:
        obj_pos = np.array([obj["x"], obj["y"]], dtype=float)
        distance_m = obj["distance"] / normalization

        if (adj_radius - 0.05) < distance_m < (adj_radius + 0.05):
            print(f"[Neutral] Skip → d={distance_m:.2f}")
            weight = 0.0
        else:
            weight = min(distance_m - adj_radius, 2.0)

            if weight < 0:
                heading *= 0
                print(f"[Repel] Close → d={distance_m:.2f}, w={weight:.2f}")
            else:
                heading *= 1
                print(f"[Attract] Far → d={distance_m:.2f}, w={weight:.2f}")

        vectors.append(weight * obj_pos)

    if not vectors:
        print("[Consensus] 유효 객체 없음. 이동 생략.")
        return None, 0.0, 1

    total_vector = np.sum(vectors, axis=0)
    magnitude = float(np.linalg.norm(total_vector))

    if magnitude == 0:
        return None, 0.0, 1

    normalized_vector = (total_vector / magnitude).tolist()
    print(f"[Debug] Total vector: {total_vector}, magnitude: {magnitude:.2f}")
    return normalized_vector, magnitude, heading


def approach_loop(state, sync, wheel_controller, communicator):
    """
    full_matrix 기반 이동 루프
    """
    while True:
        with sync["inference_lock"]:
            full_matrix = state["full_matrix"].copy()

        task_vector, magnitude, heading = compute_task_vector_with_weighted_consensus(
            full_matrix
        )

        duration = communicator.adjust_movement_based_on_consensus(wheel_controller)

        approach_with_mecanum(
            task_vector, magnitude, wheel_controller, duration, heading
        )

        time.sleep(0.05)


def gimbal_sweep_loop(ep_gimbal, state, sync):
    sweep_direction = 1

    while True:
        target_angle = -ANGLES if sweep_direction == 1 else ANGLES
        print(f"[Gimbal] Move to {target_angle}")

        try:
            ep_gimbal.moveto(
                pitch=0,
                yaw=target_angle,
                pitch_speed=30,
                yaw_speed=YAW_SPEED,
            ).wait_for_completed()
        except Exception as e:
            print(f"[Gimbal] move failed: {e}")
            try:
                ep_gimbal.recenter()
            except Exception:
                pass

        time.sleep(0.3)
        sweep_direction *= -1
