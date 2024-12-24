import socketio
import requests
import time
import json
from threading import Event


def print(*args, **kwargs):
    pass  # disable print


class DroneClient:
    def __init__(self, ip="127.0.0.1"):
        sio = socketio.Client()
        self.base_url = f"http://{ip}:9000/"
        self.sio = sio

        self.drone_id = None
        self.control_key = None
        self.data_received_event = Event()
        self.last_received_data = None

        self.velocity_updated_event = Event()
        self.last_received_veldata = None

        self.position_updated_event = Event()
        self.last_received_posdata = None

        @sio.on("connect")
        def on_connect():
            print("Connected to server")

        @sio.on("disconnect")
        def on_disconnect():
            print("Disconnected from server")

        @sio.on("drone_connected")
        def on_drone_connected(data):
            print(f"Drone connection status: {data['data']}")

        @sio.on("data_updated")
        def on_data_updated(data):
            if isinstance(data, dict):
                self.last_received_data = data
                self.data_received_event.set()

        @sio.on("velocity_updated")
        def on_velocity_updated(data):
            if isinstance(data, dict):
                self.last_received_veldata = data
                self.velocity_updated_event.set()

        @sio.on("position_updated")
        def on_position_updated(data):
            if isinstance(data, dict):
                self.last_received_posdata = data
                self.position_updated_event.set()

        @sio.on("error")
        def on_error(data):
            print(f"Error: {data['data']}")

    def wait_for_data_msg(self, timeout=None):
        self.data_received_event.clear()
        if self.data_received_event.wait(timeout):
            return self.last_received_data
        return None

    def wait_for_vel_msg(self, timeout=None):
        self.velocity_updated_event.clear()
        if self.velocity_updated_event.wait(timeout):
            return self.last_received_veldata
        return None

    def wait_for_pos_msg(self, timeout=None):
        self.position_updated_event.clear()
        if self.position_updated_event.wait(timeout):
            return self.last_received_posdata
        return None

    def create_drone(self, label=None, secret_data=None, flight_plan=None):
        response = requests.post(
            f"{self.base_url}/create_drone",
            timeout=8000,
            json={}
            | ({"label": label} if label else {})
            | ({"secret_data": secret_data} if secret_data else {})
            | ({"flight_plan": flight_plan} if flight_plan else {}),
        )
        if response.status_code == 200:
            data = response.json()
            self.drone_id = data["id"]
            self.control_key = data["control_key"]
            print(
                f"Created drone with ID: {self.drone_id}, control key: {self.control_key}"
            )
            return True
        else:
            print(f"Failed to create drone: {response.text}")
            return False

    def get_all_drones(self):
        response = requests.get(f"{self.base_url}/get_drones")
        print("All drones:", response.json())

    def get_drones_with_details(self, with_what_details):
        response = requests.get(f"{self.base_url}/get_drones?with={with_what_details}")
        return response.json()

    def connect_to_drone(self):
        try:
            self.sio.connect(self.base_url, socketio_path="/socket.io")
            self.sio.emit(
                "join_drone",
                {"drone_id": self.drone_id, "control_key": self.control_key},
            )
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def update_position(self, position):
        self.sio.emit("set_position", {"drone_id": self.drone_id, "position": position})

    def update_velocity(self, velocity):
        self.sio.emit("set_velocity", {"drone_id": self.drone_id, "velocity": velocity})

    def disconnect(self):
        try:
            self.sio.disconnect()
        except Exception as e:
            print(f"Disconnection error: {e}")
