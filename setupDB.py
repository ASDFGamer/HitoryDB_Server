import json
#wikidata
from SPARQLWrapper import SPARQLWrapper, JSON
#database
import sqlite3

#format: <client name>/<version> (<contact information>)
user_agent = "HistoryDB Server/0.1 (historyDB@christoph-wildhagen.de)"
endpoint_url = "https://query.wikidata.org/sparql"

test = True

def setupDB(conn):
	try:
		conn.execute('''CREATE TABLE IDS
			(ID 	 CHAR(50) PRIMARY KEY NOT NULL,
			PLEIADESID INT	  NOT NULL);''')
		conn.execute('''CREATE TABLE LOCATION
			(ID 	 CHAR(50) PRIMARY KEY NOT NULL,
			Latitude	 FLOAT	  NOT NULL,
			Longitude FLOAT	  NOT NULL,
			FOREIGN KEY (ID) REFERENCES IDS (ID));''')
	except:
		return False
	return True

def queryIDs():
	if not test:#Not active for testing purposes
		query = """SELECT ?article ?articleLabel ?pleiadesID  
			WHERE {
			?article wdt:P1584 ?pleiadesID . 
			} """
		sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
		sparql.setQuery(query)
		sparql.setReturnFormat(JSON)
		result =  sparql.query().convert()
		# Write result to file
		f = open("queryID.json", "w")
		f.write(json.dumps(result))
	else:
		with open('queryID.json', 'r') as openfile:
    		# Reading from json file
	 		result = json.load(openfile)

	return result

class formated_result:

	def __init__(self, wikidataID, pleiadesID):
		self.wikidataID = wikidataID
		self.pleiadesID = pleiadesID
	
	def __repr__(self): 
		return self.__str__() 

	def __str__(self): 
		return "ID {wikiID}, PleiadesID: {pleiadesID}\n".format(wikiID = self.wikidataID, pleiadesID = self.pleiadesID)
	
def formatResults(results):
	formated_results = set()
	for result in results["results"]["bindings"]:
		# print(result)
		wikidataID = result["article"]["value"].split("/")[-1]
		pleiadesID = result["pleiadesID"]["value"]
		formated_results.add(formated_result(wikidataID, pleiadesID))
	return formated_results

def insertIDs(conn, formated_results):
	for formated_result in formated_results:
		try:
			conn.execute("INSERT INTO IDS(ID, PLEIADESID) VALUES ('{}',{})".format(formated_result.wikidataID, formated_result.pleiadesID))
		except:
			print("Couldn't insert {}. Possible duplicate pleiades ID".format(formated_result.wikidataID))
			#TODO fix that multiple ids are possible
	conn.commit()

def addLocation(conn):
	if not test:
		query = """SELECT ?article ?coordinates
			WHERE {
			?article wdt:P1584 ?pleiadesID . 
			?article wdt:P625 $coordinates .
			}  """
		sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
		sparql.setQuery(query)
		sparql.setReturnFormat(JSON)
		results = sparql.query().convert()
		f = open("coordinatesWiki.json", "w")
		f.write(json.dumps(results))
	else:
		with open('coordinatesWiki.json', 'r') as openfile:
    		# Reading from json file
	 		results = json.load(openfile)
	for result in results["results"]["bindings"]:
		# print(result)
		wikidataID = result["article"]["value"].split("/")[-1]
		coordinates = result["coordinates"]["value"][6:-1]
		long_lang = coordinates.split(" ")
		if (len(long_lang) != 2):
			print(wikidataID + " has invalid coordinates")
		else:
			try:
				#TODO sql injection
				conn.execute("INSERT INTO LOCATION (ID, Longitude, Latitude) VALUES ('{}',{},{})".format(wikidataID, long_lang[0], long_lang[1]))
			except:
				print("Couldn't insert coordinates for {}. Possible duplicate coordinates".format(wikidataID))
	conn.commit()


def addData(conn):
	addLocation(conn)

def createDB(conn):
	if setupDB(conn):
		results = queryIDs()
		formated_results = formatResults(results)
		insertIDs(conn, formated_results)
		addData(conn)