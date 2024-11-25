#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
Created on 01.04.2016
@original author: micha

Updated on 24.11.2024
@author simsa 
Changed: 
 - adapted for python3
 - removed barometer sensor
 - create database table "sensor" if not exists
'''

import argparse
import logging
import math
import threading
import time
import pymysql as mdb

from davisreceiver import DavisReceiver
from util import check, sensor, description

LOOP_TIME = 60      # time between database commits


class DataLogger(object):
    def __init__(self):

        self.commit_database = False
        self.con = mdb.connect(host='localhost', database='weewx',
                               user='weewx', password='weewx', charset='latin1')
        self.cur = self.con.cursor()

        # Check if the 'sensor' table exists and create it if not
        check_table_query = "SHOW TABLES LIKE 'sensor';"
        self.cur.execute(check_table_query)

        # If the table doesn't exist, create it
        if not self.cur.fetchone():  # No results returned, table doesn't exist
            logging.info("Table 'sensor' does not exist. Creating it now...")

            create_table_query = """
            CREATE TABLE sensor (
            dateTime    BIGINT NOT NULL,
            sensor      CHAR(1) NOT NULL,
            data        VARCHAR(80),
            description VARCHAR(80),
            INDEX (dateTime),
            INDEX (sensor)
            );
            """

            self.cur.execute(create_table_query)
            logging.info("Table 'sensor' has been successfully created.")
        else:
            logging.info("Table 'sensor' already exists.")

        # Check if the 'last_sensor' table exists and create it if not
        check_table_query = "SHOW TABLES LIKE 'last_sensor';"
        self.cur.execute(check_table_query)

        # If the table doesn't exist, create it
        if not self.cur.fetchone():  # No results returned, table doesn't exist
            logging.info("Table 'last_sensor' does not exist. Creating it now...")

            create_table_query = """
            CREATE TABLE last_sensor (
                    dateTime BIGINT NOT NULL
                );
            """

            self.cur.execute(create_table_query)
            logging.info("Table 'last_sensor' has been successfully created.")
        else:
            logging.info("Table 'last_sensor' already exists.")

        self.receiver = DavisReceiver()
        self.receiver.set_handler(self.process_message)
        self.lock = threading.Lock()

    def loop(self):
        self.receiver.calibration()
        self.receiver.receive_begin()

        # main loop
        while True:
            ts = int(time.time())
            self.sleep(ts + LOOP_TIME - ts % LOOP_TIME)
            self.commit_database = True

    def sleep(self, target):
        while True:
            ts = int(time.time())
            if ts < target:
                time.sleep(target - ts)
            else:
                break

    def shutdown(self):
        if self.con:
            self.con.commit()
            self.con.close()
        if self.receiver:
            self.receiver.shutdown()

    def process_message(self, message):
        if not check(message):
            logging.warning("invalid message received: " +
                            message + " " + description(message))
            return False

        logging.debug(message + " " + description(message))
        self.store_message(message)
        return True

    def store_message(self, message):
        with self.lock:
            ts = int(time.time() * 1000)
            self.cur.execute(
                "INSERT INTO sensor(dateTime,sensor,data,description) VALUES(%s,%s,%s,%s)",
                (ts, sensor(message), message, description(message))
            )
            if self.commit_database:
                self.con.commit()
                self.commit_database = False


# the main procedure

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="more log output", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s\t%(levelname)s\t%(message)s',
                        level=logging.DEBUG if args.debug else logging.INFO)
    logging.info("Starting Davis-ISS logging")

    data_logger = None

    try:
        data_logger = DataLogger()
        data_logger.loop()
    except Exception as e:
        logging.critical(str(e))

    finally:
        logging.info("Terminating Davis-ISS logging")
        if data_logger:
            data_logger.shutdown()
