#!/usr/bin/env python3
import socket
import sys
import random
import string
import requests
import time
import json

import drone_client
import random_flight_plan
from checklib import *


def print(*args, **kwargs):
    pass  # disable print


def generate_random_datastring(length):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))

    return random_string


def percent_50():
    return random.randint(1, 2) == 1


class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 20
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(
                Status.DOWN,
                "Connection error",
                "Got requests.exceptions.ConnectionError",
            )

    def check(self):
        client = drone_client.DroneClient(ip=self.host)
        label = generate_random_datastring(random.randint(10, 30))
        client.create_drone(
            label=label, secret_data=generate_random_datastring(random.randint(10, 30))
        )
        time.sleep(1)
        
        client.connect_to_drone()
        vel = [random.randint(-3, 3), random.randint(-3, 3)]
        pos = [random.randint(-20, 20), random.randint(-20, 20)]
        client.update_velocity(vel)
        vel_msg = client.wait_for_vel_msg(timeout=30)
        self.assert_eq(
            vel, vel_msg["new_velocity"], "Incorrect velocity handling", Status.CORRUPT
        )

        client.update_position(pos)
        pos_msg = client.wait_for_pos_msg(timeout=30)
        self.assert_eq(
            pos, pos_msg["new_position"], "Incorrect position handling", Status.CORRUPT
        )

        drone_obj = client.wait_for_data_msg(timeout=30)
        for _ in range(5):
            if vel == drone_obj["velocity"]:
                break
            drone_obj = client.wait_for_data_msg(timeout=30)
        
        self.assert_eq(
            vel, drone_obj["velocity"], "Incorrect velocity handling", Status.CORRUPT
        )
        
        drone_obj_via_httpapi = client.get_drones_with_details(
            json.dumps([{"$match": {"label": label}}])
        )[0]
        self.assert_eq(
            drone_obj_via_httpapi["label"],
            label,
            "Incorrect HTTP API response",
            Status.CORRUPT,
        )
        self.assert_eq(
            drone_obj_via_httpapi["velocity"],
            vel,
            "Incorrect HTTP API response",
            Status.CORRUPT,
        )
        self.assert_eq(
            drone_obj_via_httpapi["id"],
            drone_obj["id"],
            "Incorrect HTTP API response",
            Status.CORRUPT,
        )

        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        fp = "\n".join(random_flight_plan.generate_plan(4, 7))
        client = drone_client.DroneClient(ip=self.host)
        client.create_drone(
            label=generate_random_datastring(random.randint(10, 30)),
            secret_data=flag,
            flight_plan=fp,
        )
        self.cquit(
            Status.OK,
            f"{client.drone_id}",
            json.dumps(
                {
                    "drone_id": client.drone_id,
                    "control_key": client.control_key,
                    "flight_plan": fp,
                }
            ),
        )

    def get(self, flag_id: str, flag: str, vuln: str):
        # print('get FLAG by!', flag_id, '!!<-id')
        drone = json.loads(flag_id)

        if vuln == "1":
            client = drone_client.DroneClient(ip=self.host)
            client.drone_id = drone["drone_id"]
            client.control_key = drone["control_key"]
            client.connect_to_drone()

            drone_obj = client.wait_for_data_msg(timeout=30)
            expected_fl = random_flight_plan.get_expected_flight_log(
                drone["flight_plan"], drone_obj["cur_time"], drone_obj
            )
            real_fl = drone_obj["flight_log"]
            self.assert_eq(
                sorted(expected_fl.split("\n")),
                sorted(real_fl.split("\n")),
                "Incorrect flight log",
                Status.CORRUPT,
            )
            self.assert_eq(
                flag, drone_obj["secret_data"], "Incorrect flag", Status.CORRUPT
            )

        self.cquit(Status.OK)


# if __name__ == '__main__':
# c = Checker("127.0.0.1")
# try:
# c.action("put", "", "TestFLAG234Fofkdjfn", "1")
# c.action("get",r'{"drone_id": "6756e4e9fb6b9f5011e88fa8", "control_key": "c3ff78e2", "flight_plan": "7 BOOSTY [drone] 1\n7 BOOSTX [drone] -1\n7 BOOSTX [drone] -2\n13 BOOSTY [drone] 2\n5 BOOSTY [drone] -1\n10 BOOSTY [drone] 2\n10 FIRE [drone]"}', "TestFLAG234Fofkdjfn", "1")
# c.action("check")
# except c.get_check_finished_exception():
# cquit(Status(c.status), c.public, c.private)
if __name__ == "__main__":
    c = Checker(sys.argv[2])
    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
