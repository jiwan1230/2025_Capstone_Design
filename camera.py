# camera.py

import time
from datetime import datetime

from estimation import undistort_image


def gimbal_angle_callback(angle_info, state, sync):
    """
    RoboMaster gimbal angle callback
    angle_info: (_, yaw_angle, _, _)
    """
    _, yaw_angle, _, _ = angle_info
    with sync["inference_lock"]:
        state["now_theta"] = yaw_angle


def chassis_attitude_callback(attitude, state):
    """
    RoboMaster chassis attitude callback
    attitude[2] -> yaw
    """
    state["chassis_yaw"] = attitude[2]


def capture_camera(ep_camera, state, sync, K, dist):
    """
    카메라 프레임을 읽어서 왜곡 보정 후 shared_frame에 저장
    """
    print("[Camera] start_video_stream 시작")
    ep_camera.start_video_stream(display=False, resolution="720p")

    while True:
        frame = ep_camera.read_cv2_image(strategy="newest")

        if frame is None:
            print("[Warning] Camera frame is None, attempting to restart stream")
            ep_camera.stop_video_stream()
            time.sleep(0.07)
            ep_camera.start_video_stream(display=False, resolution="720p")
            continue

        try:
            corrected = undistort_image(frame, K, dist)
        except Exception as e:
            print(f"[Camera] undistort failed: {e}")
            corrected = frame

        with sync["inference_lock"]:
            state["shared_frame"] = corrected

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] camera 동작중")
        time.sleep(0.05)
