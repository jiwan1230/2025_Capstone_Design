# communication.py

import json
import socket
import time

from config import UDP_IP, UDP_PORT, MAX_CONFIRM_THRESHOLD, MAX_RESET_TIMEOUT, DURATION


class ConsensusCommunicator:
    def __init__(self):
        self.max_count = 0
        self.count_history = []
        self.last_max_update_time = time.time()
        self.received_max_counts = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(0.1)
        self.sock.bind(("", UDP_PORT))

    def update_max_count(self, local_full_matrix):
        current_count = len(local_full_matrix)
        self.count_history.append(current_count)

        if len(self.count_history) > MAX_CONFIRM_THRESHOLD:
            self.count_history.pop(0)

        if (
            len(set(self.count_history)) == 1
            and len(self.count_history) == MAX_CONFIRM_THRESHOLD
        ):
            self.max_count = self.count_history[0]
            self.last_max_update_time = time.time()
            print(f"[Max Updated] max_count = {self.max_count}")

        if (
            time.time() - self.last_max_update_time > MAX_RESET_TIMEOUT
            and current_count != self.max_count
        ):
            self.max_count = current_count
            self.count_history.clear()
            self.last_max_update_time = time.time()
            print(f"[Max Reset] max_count = {self.max_count}")

        self.broadcast_max_count()
        print(
            f"[Debug] current_count = {current_count}, "
            f"count_history = {self.count_history}, "
            f"max_count = {self.max_count}"
        )

    def broadcast_max_count(self):
        message = json.dumps({"max_count": self.max_count})
        try:
            self.sock.sendto(message.encode(), (UDP_IP, UDP_PORT))
            print(f"[Broadcast] Sent max_count = {self.max_count}")
        except Exception as e:
            print(f"[Error] Broadcast failed: {e}")

    def receive_max_counts(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(1024)
                message = json.loads(data.decode())
                received_count = message["max_count"]

                self.received_max_counts.append(received_count)
                if len(self.received_max_counts) > 3:
                    self.received_max_counts.pop(0)

                print(f"[Received] max_count = {received_count}")
                print(f"[Received] received_max_counts = {self.received_max_counts}")
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[Error] Receive failed: {e}")
                continue

    def adjust_movement_based_on_consensus(self, wheel_controller):
        if not self.received_max_counts:
            print("[Consensus] No received max_counts, using default settings")
            wheel_controller.MAX_RPM = 100
            wheel_controller.MIN_RPM = 50
            return DURATION

        try:
            max_received = max(self.received_max_counts)
            min_received = min(self.received_max_counts)

            print(
                f"[Consensus] My max_count = {self.max_count}, "
                f"Max received = {max_received}, Min received = {min_received}"
            )

            if self.max_count >= max_received and self.max_count > min_received:
                print("[Consensus] My max_count is largest, reducing movement")
                wheel_controller.MAX_RPM = 50
                wheel_controller.MIN_RPM = 10
                return DURATION * 0.3
            else:
                print("[Consensus] Using default settings")
                wheel_controller.MAX_RPM = 100
                wheel_controller.MIN_RPM = 50
                return DURATION

        except ValueError:
            print(
                f"[Error] Invalid data in received_max_counts: {self.received_max_counts}"
            )
            self.received_max_counts.clear()
            wheel_controller.MAX_RPM = 100
            wheel_controller.MIN_RPM = 20
            return DURATION

    def close(self):
        self.sock.close()
