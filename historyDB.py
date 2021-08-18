#!/usr/bin/env python3
#This is only a very basic server.
#It should be replaced by something better, for example something that is backed by sawagger/openAPI

import sys
import os
from os.path import dirname, realpath

#This has to be done so that other files in the same folder can be found.
sys.path.insert(0, realpath(dirname(__file__)))

#webserver
from flask import Flask, request, jsonify

#Location String parsing
import json
#database
import sqlite3

import setupDB
dbname = "db.sqlite"
conn = sqlite3.connect(dbname)

app = Flask("historyDB")

@app.route("/v1/")
def home():
	return  {'title':'HistoryDB', 'version': 0.1}

@app.route("/v1/stats")
def stats():
	return {
		'objects':countObjects(),
		'coordinates': countCoordinates()
	}

@app.route("/v1/location", methods=['GET'])
def findLocation():
	#[[38.41719605, 27.141387], [38.41719605, 27.141387]]
	if not request.args.get('location'):
		return "Please Provide a location"
	location = json.loads(request.args.get('location'))
	results = findLocations(location[0], location[1])
	return jsonify(results)
	
def findLocations(corner1, corner2):
	conn = sqlite3.connect(dbname)
	highLangitude = max(corner1[0], corner2[0])
	lowLangitude = min(corner1[0], corner2[0])
	highLongitude = max(corner1[1], corner2[1])
	lowLongitude = min(corner1[1], corner2[1])
	results = []
	cursor = conn.execute("SELECT i.* FROM IDS i LEFT JOIN LOCATION l on l.ID = i.ID WHERE l.Longitude >= {} AND l.Longitude <= {} AND l.Latitude >= {} AND l.Latitude <= {};".format(lowLongitude, highLongitude, lowLangitude, highLangitude))
	for row in cursor:
		results.append({
			"wikidata_id": row[0], 
			"pleiades_id": row[1]
			})
	return results

def countObjects():
	conn = sqlite3.connect(dbname)
	cursor = conn.execute("SELECT Count(*) FROM IDS")
	for row in cursor:
		print(row)
		result = row[0]
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