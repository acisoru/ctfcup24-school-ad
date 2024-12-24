#!/usr/bin/python3
import psycopg2
import sys

class LocalDb:
    def __init__(self):
        pass

    def connect(self,conn_string):
        #try:
        self.conn = psycopg2.connect(
                conn_string
        )
        #except Exception as e:
        #print(e)

    def execute(self, command):
        cursor = self.conn.cursor()
        #try:
        cursor.execute(command)
        try:
            result = cursor.fetchall()
        except Exception as e:
            print(e,file=sys.stderr)
            result = []
        #cursor.close()
        return result

    def disconnect(self):
        self.conn.cursor.close()
        self.conn.close()
