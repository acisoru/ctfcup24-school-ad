#!/usr/bin/env python3

import sys
import requests
import json
from checklib import *
from filtranator import *


def strcmp(str1,str2):
    if (len(str1) != len(str2)):
        return False
    for i in range(len(str1)):
        if(str1[i] != str2[i]):
            if((str1[i] in os and str2[i] in os) or (str1[i] in ixs and str2[i] in ixs)  or (str1[i] in qs and str2[i] in qs)):
               continue
            else:
                return False
    return True

class Checker(BaseChecker):
    vulns: int = 1
    timeout: int = 10
    uses_attack_data: bool = True

    def __init__(self, *args, **kwargs):
        super(Checker, self).__init__(*args, **kwargs)
        self.mch = CheckMachine(self)

    def action(self, action, *args, **kwargs):
        try:
            super(Checker, self).action(action, *args, **kwargs)
        except requests.exceptions.ConnectionError:
            self.cquit(Status.DOWN, "Connection error", "Got requests connection error")

    def check(self):
        session = get_initialized_session()
        username, password = rnd_username(), rnd_password()

        self.mch.register(session, username, password, Status.MUMBLE)
        self.mch.login(session, username, password, Status.MUMBLE)
        img_value = rnd_string(20).upper()
        self.mch.put_image(session,img_value,Status.MUMBLE)
        value = self.mch.get_image(session)
        self.assert_(img_value.replace('0','O').replace('1','I').replace('l','I'), value.replace('0','O').replace('1','I').replace('l','I'), Status.MUMBLE)
        self.mch.logout(session,Status.MUMBLE)
        self.cquit(Status.OK)

    def put(self, flag_id: str, flag: str, vuln: str):
        session = get_initialized_session()
        username, password = rnd_username(), rnd_password()

        self.mch.register(session, username, password, Status.MUMBLE)
        self.mch.login(session, username, password, Status.MUMBLE)
        self.mch.put_image(session, flag, Status.MUMBLE)
        self.mch.logout(session, Status.MUMBLE)
        self.cquit( Status.OK,public=json.dumps({"username":username}),
            private=f"{username}:{password}",
        )

    def get(self, flag_id: str, flag: str, vuln: str):
        s = get_initialized_session()
        username, password = flag_id.split(":")
        self.mch.login(s, username, password, Status.CORRUPT)
        value = self.mch.get_image(s)
        self.mch.logout(s, Status.CORRUPT)
        self.assert_(value.upper().replace('0','O').replace('1','I').replace('l','I'), flag.upper().replace('0','O').replace('1','I').replace('l','I'), Status.CORRUPT)
        self.cquit(Status.OK)


if __name__ == "__main__":
    c = Checker(sys.argv[2])

    try:
        c.action(sys.argv[1], *sys.argv[3:])
    except c.get_check_finished_exception():
        cquit(Status(c.status), c.public, c.private)
