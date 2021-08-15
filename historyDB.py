#!/usr/bin/env python3
#This is only a very basic server.
#It should be replaced by something better, for example something that is backed by sawagger/openAPI

import sys
import os
from os.path import dirname, realpath

#This has to be done so that other files in the same folder can be found.
sys.path.insert(0, realpath(os.path.join(dirname(__file__), '../')))

#webserver
from flask import Flask
#database
import sqlite3

import setupDB

conn = sqlite3.connect(':memory:')

app = Flask("historyDB")

@app.route("/v1/")
def hello_world():
	return  {'title':'HistoryDB', 'version': 0.1}


if __name__ == "__main__":
	setupDB.createDB(conn)
	app.run()
	conn.close()