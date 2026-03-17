# # config 파일 test
# from config import f_w, F_W, MODEL_PATH, CALIB_PATH, ADJ_RADIUS

# print(f_w, F_W, MODEL_PATH, CALIB_PATH, ADJ_RADIUS)

# --------------------

# # utils 파일 test
# from utils import select_f_and_size, interpolate_object

# print(select_f_and_size(0.7))
# print(select_f_and_size(0.9))
# print(select_f_and_size(1.2))

# a = {
#     "distance": 1000.0,
#     "theta": 10.0,
#     "x": 100.0,
#     "y": 900.0,
#     "dx": -20.0,
#     "confidence": 0.9,
#     "label": "W",
#     "aspect": 0.7,
# }
# b = {
#     "distance": 1100.0,
#     "theta": 12.0,
#     "x": 120.0,
#     "y": 950.0,
#     "dx": 15.0,
#     "confidence": 0.95,
#     "label": "W",
#     "aspect": 0.72,
# }
# print(interpolate_object(a, b))

# --------------------------
# # estimate test
# from estimation import load_calibration
# from estimation import estimate_local_coordinates


# K, dist = load_calibration()
# print(K.shape, dist.shape)

# x, y, theta = estimate_local_coordinates(
#     distance=1000, dx_px=100, yaw_angle=10, focal_length=482
# )
# print(x, y, theta)

# --------------------------

# # camera.py test

# from camera import gimbal_angle_callback, chassis_attitude_callback

# state = {
#     "now_theta": 0.0,
#     "chassis_yaw": 0.0,
#     "shared_frame": None,
# }

# import threading

# sync = {"inference_lock": threading.Lock()}

# gimbal_angle_callback((0, 15.5, 0, 0), state, sync)
# chassis_attitude_callback((0, 0, 33.3), state)

# print(state["now_theta"])
# print(state["chassis_yaw"])

# ---------------------------

# # inference 파일 테스트

# from inference import create_model

# model = create_model()
# print(type(model))

# ---------------------------
# # smoothing 파일 테스트
# import threading
# from smoothing import save_or_update_object

# state = {
#     "full_matrix": [],
# }

# sync = {"inference_lock": threading.Lock()}

# obj1 = {
#     "x": 100.0,
#     "y": 200.0,
#     "theta": 10.0,
#     "distance": 1000.0,
#     "dx": -20.0,
#     "confidence": 0.9,
#     "label": "W",
#     "aspect": 0.7,
#     "timestamp": "2026-03-17_17-40-00-000",
# }

# obj2 = {
#     "x": 110.0,
#     "y": 205.0,
#     "theta": 12.0,
#     "distance": 1010.0,
#     "dx": -18.0,
#     "confidence": 0.95,
#     "label": "W",
#     "aspect": 0.72,
#     "timestamp": "2026-03-17_17-40-01-000",
# }

# save_or_update_object(obj1, state, sync)
# save_or_update_object(obj2, state, sync)

# print(len(state["full_matrix"]))
# print(state["full_matrix"])

# -------------------------------------

# from communication import ConsensusCommunicator


# class DummyWheel:
#     def __init__(self):
#         self.MAX_RPM = 0
#         self.MIN_RPM = 0


# comm = ConsensusCommunicator()

# wheel = DummyWheel()

# comm.update_max_count([1, 2, 3])
# comm.update_max_count([1, 2, 3])

# print("max_count:", comm.max_count)

# comm.received_max_counts = [1, 2, 2]
# duration = comm.adjust_movement_based_on_consensus(wheel)

# print("duration:", duration)
# print("MAX_RPM:", wheel.MAX_RPM)
# print("MIN_RPM:", wheel.MIN_RPM)

# comm.close()

# ----------------------------------------


# from control import MecanumWheelController, compute_task_vector_with_weighted_consensus


# class DummyChassis:
#     def drive_wheels(self, w1, w2, w3, w4):
#         print("drive_wheels:", w1, w2, w3, w4)


# full_matrix = [
#     {
#         "x": 100.0,
#         "y": 900.0,
#         "distance": 1200.0,
#         "theta": 10.0,
#         "dx": -20.0,
#         "confidence": 0.9,
#         "label": "W",
#         "aspect": 0.7,
#         "timestamp": "2026-03-17_18-00-00-000",
#     },
#     {
#         "x": -120.0,
#         "y": 850.0,
#         "distance": 650.0,
#         "theta": -8.0,
#         "dx": 15.0,
#         "confidence": 0.95,
#         "label": "W",
#         "aspect": 0.72,
#         "timestamp": "2026-03-17_18-00-01-000",
#     },
# ]

# task_vector, magnitude, heading = compute_task_vector_with_weighted_consensus(
#     full_matrix
# )
# print("task_vector:", task_vector)
# print("magnitude:", magnitude)
# print("heading:", heading)

# wheel = MecanumWheelController(DummyChassis())
# rpm = wheel.calc_wheel_rpm(task_vector, magnitude, heading)
# print("rpm:", rpm)


# -----------------------------

# from control import approach_loop

# # 실제 실행 X → 구조 확인용
# print("control loop import OK")

# -----------------------------
