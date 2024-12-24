from flask import Flask, request, jsonify, abort
from flask_socketio import SocketIO, join_room
from pymongo import MongoClient
from bson import ObjectId
import os
import time
from datetime import datetime, timedelta
import gevent
import json
import session_authenticator
from flight_plans import process_flight_plan
from functools import partial
import misc
from gevent.lock import BoundedSemaphore
db_lock = BoundedSemaphore(1)
app = Flask(__name__)
socketio = SocketIO(app)

client = MongoClient(os.getenv("MONGO_URI"))
db = client["drone_db"]
drones_collection = db["drones"]

misc.initialize(drones_collection)


DRONE_LIFETIME = 8 * 60  # in seconds


@app.route("/create_drone", methods=["POST"])
def create_drone():
    with db_lock:
        label = request.json.get("label", "NO_LABEL")
        secret_data = request.json.get("secret_data", "")
        flight_plan = request.json.get("flight_plan", "")

        creation_time = datetime.now()
        drone = {
            "label": label,
            "position": [0, 0],
            "velocity": [0, 0],
            "control_key": "",
            "flight_plan": flight_plan,
            "flight_log": "",
            "secret_data": secret_data,
            "created_at": creation_time,
            "expires_at": creation_time + timedelta(seconds=DRONE_LIFETIME),
        }

        result = drones_collection.insert_one(drone)
        drone_id = str(result.inserted_id)
        control_key = session_authenticator.generate(drone_id, label)

        drones_collection.update_one(
            {"_id": result.inserted_id}, {"$set": {"control_key": control_key}}
        )

        return jsonify(
            {
                "id": drone_id,
                "control_key": control_key,
                "expires_at": drone["expires_at"].isoformat(),
            }
        )


def filter_sensitive_data(
    data, filtered_fields=["control_key", "secret_data", "flight_plan", "flight_log"]
):
    if isinstance(data, list):
        return [filter_sensitive_data(item) for item in data]
    elif isinstance(data, dict):
        return {k: v for k, v in data.items() if k not in filtered_fields}
    return data


@app.route("/get_drones", methods=["GET"])
def get_drones():
    with db_lock:
        with_field = request.args.get("with")
        if with_field:
            projection = json.loads(with_field)
            if len(projection[0]) == 1 and list(projection[0].keys())[0] == "$match":
                drones_response = list(drones_collection.aggregate(projection))

                drones_response_final = []
                for item in drones_response:
                    new_dict = item.copy()
                    new_dict["id"] = str(new_dict["_id"])
                    del new_dict["_id"]
                    drones_response_final.append(new_dict)

                return json.dumps(filter_sensitive_data(drones_response_final), default=str)
            return abort(403)
        else:
            drones_cursor = drones_collection.find({}, {"_id": 1})
            return json.dumps(
                [{"id": str(drone["_id"])} for drone in drones_cursor], default=str
            )


@socketio.on("connect")
def connect():
    print("Client connected")


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected")


@socketio.on("join_drone")
def join_drone(data):
    with db_lock:
        drone_id = data["drone_id"]
        control_key = data["control_key"]

        drone = drones_collection.find_one({"_id": ObjectId(drone_id)})

        if drone and drone["control_key"] == control_key:
            join_room(drone_id)
            socketio.emit(
                "drone_connected", {"data": f"Connected to drone {drone_id}"}, room=drone_id
            )
        else:
            socketio.emit("error", {"data": "Invalid drone ID or control key"})


@socketio.on("set_position")
def set_position(data):
    with db_lock:
        drone_id = data["drone_id"]
        position = data["position"]

        drones_collection.update_one(
            {"_id": ObjectId(drone_id)}, {"$set": {"position": position}}
        )

        socketio.emit(
            "position_updated",
            {"id": drone_id, "new_position": position},
            room=drone_id,
        )


@socketio.on("set_velocity")
def set_velocity(data):
    with db_lock:
        drone_id = data["drone_id"]
        velocity = data["velocity"]

        drones_collection.update_one(
            {"_id": ObjectId(drone_id)}, {"$set": {"velocity": velocity}}
        )

        socketio.emit(
            "velocity_updated",
            {"id": drone_id, "new_velocity": velocity},
            room=drone_id,
        )


def update_positions():
    with db_lock:
        current_time = datetime.now()

        expired_drones = drones_collection.find({"expires_at": {"$lt": current_time}})
        for drone in expired_drones:
            drone_id = str(drone["_id"])
            drones_collection.delete_one({"_id": drone["_id"]})
            socketio.emit("drone_expired", {"id": drone_id}, room=str(drone["_id"]))

        active_drones = drones_collection.find({"expires_at": {"$gt": current_time}})

        for drone in active_drones:
            cur_time = (datetime.now() - drone["created_at"]).total_seconds()
            process_flight_plan(drone, cur_time)
            new_position = [
                drone["position"][0] + drone["velocity"][0],
                drone["position"][1] + drone["velocity"][1],
            ]
            new_velocity = drone["velocity"].copy()

            for i in range(2):
                if abs(new_position[i]) > 100:
                    new_velocity[i] = -new_velocity[i]
                    new_position[i] = 100 if new_position[i] > 0 else -100

            drones_collection.update_one(
                {"_id": drone["_id"]},
                {"$set": {"position": new_position, "velocity": new_velocity}},
            )
            socketio.emit(
                "data_updated",
                {
                    "id": str(drone["_id"]),
                    "label": drone["label"],
                    "position": new_position,
                    "velocity": new_velocity,
                    "cur_time": int(cur_time),
                    "control_key": drone["control_key"],
                    "flight_plan": drone["flight_plan"],
                    "flight_log": drone["flight_log"],
                    "secret_data": drone["secret_data"],
                    "created_at": str(drone["created_at"]),
                    "expires_at": str(drone["expires_at"]),
                },
                room=str(drone["_id"]),
            )


def run_update_positions():
    print("start_background_task")
    while True:
        update_positions()
        gevent.sleep(1)


socketio.start_background_task(run_update_positions)
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=9001)
