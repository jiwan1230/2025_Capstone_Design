# main.py

import time
import threading
from functools import partial

from robomaster import robot as rm_robot

from estimation import load_calibration
from inference import create_model, run_yolo_loop
from camera import (
    gimbal_angle_callback,
    chassis_attitude_callback,
    capture_camera,
)
from smoothing import smoothing_loop
from communication import ConsensusCommunicator
from control import (
    MecanumWheelController,
    approach_loop,
    gimbal_sweep_loop,
)


def create_state():
    return {
        "now_theta": 0.0,
        "chassis_yaw": 0.0,
        "shared_frame": None,
        "shared_yolo_matrix": [],
        "full_matrix": [],
        "candidate_buffer": [],
        "results_list": [],
        "prev_dx": None,
        "prev_sign": None,
    }


def create_sync():
    return {
        "inference_lock": threading.Lock(),
    }


def build_threads(
    ep_camera, ep_gimbal, wheel_controller, state, sync, K, dist, model, communicator
):
    return [
        threading.Thread(
            target=capture_camera,
            args=(ep_camera, state, sync, K, dist),
            daemon=True,
            name="CameraCapture",
        ),
        threading.Thread(
            target=run_yolo_loop,
            args=(state, sync, model),
            daemon=True,
            name="YoloLoop",
        ),
        threading.Thread(
            target=smoothing_loop,
            args=(state, sync),
            daemon=True,
            name="SmoothingLoop",
        ),
        threading.Thread(
            target=communicator.receive_max_counts,
            daemon=True,
            name="CommReceive",
        ),
        threading.Thread(
            target=approach_loop,
            args=(state, sync, wheel_controller, communicator),
            daemon=True,
            name="ApproachLoop",
        ),
        threading.Thread(
            target=gimbal_sweep_loop,
            args=(ep_gimbal, state, sync),
            daemon=True,
            name="GimbalSweep",
        ),
    ]


def main():
    state = create_state()
    sync = create_sync()

    K, dist = load_calibration()
    model = create_model()
    communicator = ConsensusCommunicator()

    ep = rm_robot.Robot()

    try:
        ep.initialize(conn_type="sta", sn="159CJC400700MW")

        ep_camera = ep.camera
        ep_gimbal = ep.gimbal
        ep_chassis = ep.chassis

        wheel_controller = MecanumWheelController(ep_chassis)

        ep_gimbal.sub_angle(
            freq=10,
            callback=partial(gimbal_angle_callback, state=state, sync=sync),
        )
        ep_chassis.sub_attitude(
            freq=10,
            callback=partial(chassis_attitude_callback, state=state),
        )

        threads = build_threads(
            ep_camera=ep_camera,
            ep_gimbal=ep_gimbal,
            wheel_controller=wheel_controller,
            state=state,
            sync=sync,
            K=K,
            dist=dist,
            model=model,
            communicator=communicator,
        )

        for t in threads:
            t.start()

        print("[Main] all threads started")

        while True:
            print(
                f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"[Debug] Thread status: "
                f"{[f'{t.name}: {t.is_alive()}' for t in threads]}"
            )
            time.sleep(5)

    except KeyboardInterrupt:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [Main] 종료 요청 감지")

    finally:
        try:
            communicator.close()
        except Exception:
            pass

        try:
            ep.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
