#!/usr/bin/env python3
#This is only a very basic server.
#It should be replaced by something better, for example something that is backed by sawagger/openAPI

import sys
import os
from os.path import dirname, realpath

#This has to be done so that other files in the same folder can be found.
sys.path.insert(0, realpath(dirname(__file__)))

#webserver
from flask import Flask
#database
import sqlite3

import setupDB
dbname = "db.sqlite"
conn = sqlite3.connect(dbname)

app = Flask("historyDB")

@app.route("/v1/")
def hello_world():
	return  {'title':'HistoryDB', 'version': 0.1}

@app.route("/v1/stats")
def stats():
	return {
		'objects':countObjects(),
		'coordinates': countCoordinates()
	}


def countObjects():
	conn = sqlite3.connect(dbname)
	cursor = conn.execute("SELECT Count(*) FROM IDS")
	for row in cursor:
		print(row)
		result  =row[0]
	conn.close()
	return row[0]

def countCoordinates():
	conn = sqlite3.connect(dbname)
	cursor = conn.execute("SELECT Count(*) FROM LOCATION")
	for row in cursor:
		print(row)
		result = row[0]
	conn.close()
	
	return result

if __name__ == "__main__":
	setupDB.createDB(conn)
	conn.close()
	app.run(debug=True)