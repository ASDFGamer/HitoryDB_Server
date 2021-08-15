#!/usr/bin/env python3
#This is only a very basic server.
#It should be replaced by something better, for example something that is backed by sawagger/openAPI

import sys

import json
#webserver
from flask import Flask
#wikidata
from SPARQLWrapper import SPARQLWrapper, JSON
#database
import sqlite3

conn = sqlite3.connect(':memory:')
#format: <client name>/<version> (<contact information>)
user_agent = "HistoryDB Server/0.1 (historyDB@christoph-wildhagen.de)"
endpoint_url = "https://query.wikidata.org/sparql"
app = Flask("historyDB")

@app.route("/v1/")
def hello_world():
	return  {'title':'HistoryDB', 'version': 0.1}

def setupDB(conn):
	conn.execute('''CREATE TABLE IDS
		(ID 	 CHAR(50) PRIMARY KEY NOT NULL,
		NAME	 TEXT	  NOT NULL,
		PLEIADESID INT	  NOT NULL);''')
	conn.execute('''CREATE TABLE LOCATION
		(ID 	 CHAR(50) PRIMARY KEY NOT NULL,
		LATITUDE	 TEXT	  NOT NULL,
		LONGITUDE INT	  NOT NULL);''')

def queryIDs():
	if 1 == 0:#Not active for testing purposes
		query = """SELECT ?article ?articleLabel ?pleiadesID  
			WHERE {
			?article wdt:P1584 ?pleiadesID . 
			SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } 
			} """
		sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
		sparql.setQuery(query)
		sparql.setReturnFormat(JSON)
		result =  sparql.query().convert()
		# Write result to file
		# f = open("queryID.json", "w")
		# f.write(json.dumps(result))
	else:
		with open('queryID.json', 'r') as openfile:
    		# Reading from json file
	 		result = json.load(openfile)

	return result

class formated_result:

	def __init__(self, wikidataID, name, pleiadesID):
		self.wikidataID = wikidataID
		self.name = name
		self.pleiadesID = pleiadesID
	
	def __repr__(self): 
		return self.__str__() 

	def __str__(self): 
		return "ID {wikiID} ({name}), PleiadesID: {pleiadesID}\n".format(wikiID = self.wikidataID, name = self.name, pleiadesID = self.pleiadesID)
	
def formatResults(results):
	formated_results = set()
	for result in results["results"]["bindings"]:
		# print(result)
		wikidataID = result["article"]["value"].split("/")[-1]
		name = result["articleLabel"]["value"]
		pleiadesID = result["pleiadesID"]["value"]
		formated_results.add(formated_result(wikidataID, name, pleiadesID))
	return formated_results

def insertIDs(conn, formated_results):
	for formated_result in formated_results:
		print("INSERT INTO IDS(ID, NAME, PLEIADESID) VALUES ({},{},{})".format(formated_result.wikidataID, formated_result.name, formated_result.pleiadesID))
	conn.commit()

def addLocation(conn):
	query = """SELECT ?article ?coordinates
		WHERE {
		  ?article wdt:P1584 ?pleiadesID . 
		  ?article wdt:P625 $coordinates .
		}  """
	sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
	sparql.setQuery(query)
	sparql.setReturnFormat(JSON)
	results = sparql.query().convert()
	for result in results["results"]["bindings"]:
		# print(result)
		wikidataID = result["article"]["value"].split("/")[-1]
		coordinates = result["coordinates"]["value"][6:-1]
		long_lang = coordinates.split(" ")
		if (len(long_lang) != 2):
			print(wikidataID + " has invalid coordinates")
		else:
			conn.execute("INSERT INTO IDS(ID, LONGITUDE, LANGITUDE) VALUES ({},{},{})".format(wikidataID, long_lang[0], long_lang[1]))

def addData(conn):
	addLocation(conn)

def createDB(conn):
	setupDB(conn)
	results = queryIDs()
	formated_results = formatResults(results)
	insertIDs(conn, formated_results)
	addData(conn)
	

if __name__ == "__main__":
	createDB(conn)
	app.run()
	conn.close()