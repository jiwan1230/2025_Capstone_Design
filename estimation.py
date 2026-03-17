# estimation.py

import math
import cv2
import numpy as np

from config import CALIB_PATH, f_w


def load_calibration(calib_path=CALIB_PATH):
    data = np.load(calib_path)
    K = data["K"]
    dist = data["dist"]
    return K, dist


def undistort_image(image, K, dist):
    h, w = image.shape[:2]
    newK, roi = cv2.getOptimalNewCameraMatrix(K, dist, (w, h), 0, (w, h))
    undst = cv2.undistort(image, K, dist, None, newK)

    x, y, w_roi, h_roi = roi
    undst = undst[y : y + h_roi, x : x + w_roi]
    return undst


def estimate_local_coordinates(distance, dx_px, yaw_angle, focal_length=None):
    if focal_length is None:
        focal_length = f_w

    if distance == 0:
        return 0.0, 0.0, float(yaw_angle)

    dx_mm = dx_px * distance / focal_length
    ratio = dx_mm / distance
    ratio = min(1.0, max(-1.0, ratio))

    theta_rad = math.asin(ratio)
    local_theta = math.radians(yaw_angle) + theta_rad

    x = distance * math.sin(local_theta)
    y = distance * math.cos(local_theta)

    return x, y, math.degrees(local_theta)
