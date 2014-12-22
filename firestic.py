# FireStic - Python script for indexing FireEye json alerts 
# into Elasticsearch over http...and some alerting too
#
# Please see: https://github.com/gnonai/firestic
# 
from datetime import datetime
from elasticsearch import Elasticsearch
from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
import json
import logging
import pygeoip  	 # pip install pygeoip
import socket
import firestic_alert

# ---------------------------------------------
# config --> TODO: move this to another file
esIndex = 'firestic'	 			# Elasticsearch index to use - YYYY.MM.DD will be appended
extGeoipDatabase = 'geoip/GeoLiteCity.dat'	# Geoip database for external (internet) addresses
intGeoipDatabase = 'geoip/GeoLiteCity.dat'	# Geoip database for internal (LAN) addresses (see README)
ASNGeoipDatabase = 'geoip/GeoIPASNum.dat'	# Geoip database for external address ASN info
localASN = 'your_org_name'			# ASN for internal addresses
httpServerIP = 'ipa.dd.re.ss'			# IP for http server to listen on
httpServerPort = 8888				# Port for http server to listen on
logFile = 'firestic_error.log'			# File for logging errors
sendAlerts = True				# Send email/SMS alerts - see firestic_alert.py
# ---------------------------------------------

class MyRequestHandler (BaseHTTPRequestHandler) :

    # ---------- GET handler to check if httpserver up ----------
    def do_GET(self) :
	pingresponse = {"name":"Firestic is up"}
        if self.path == "/ping" :
            	self.send_response(200)
            	self.send_header("Content-type:", "text/html")
            	self.wfile.write("\n")
            	json.dump(pingresponse, self.wfile)

    # -------------------- POST handler: where the magic happens --------------------
    def do_POST (self) :
	# get the posted data and remove newlines
	data = self.rfile.read(int(self.headers.getheader('Content-Length')))
       	clean = data.replace('\n','')       
       	theJson = json.loads(clean)

	self.send_response(200)
       	self.end_headers()
	
	# deal with multiple alerts embedded as an array
	if isinstance(theJson['alert'],list):
		alertJson = theJson
		del alertjson['alert']
		for element in theJson['alert']:
			alertJson['alert'] = element
			processAlert(alertJson)
	else:
		processAlert(theJson)

# ----------------------------- end class MyRequestHandler -----------------------------

def processAlert(theJson):
	# ---------- add geoip information ----------
	alertInfo = {}
	alertInfo['srcIp'] = theJson['alert'].setdefault('src',{}).setdefault(u'ip',u'0.0.0.0')
	alertInfo['dstIp'] = theJson['alert'].setdefault('dst',{}).setdefault(u'ip',u'0.0.0.0')

	alertInfo['type'] = theJson['alert']['name']
	if alertInfo['type'] == 'ips-event':
		alertInfo['mode'] = theJson['alert']['explanation']['ips-detected']['attack-mode']
	
	geoInfo = queryGeoip(alertInfo)

	theJson['alert']['src']['geoip'] = geoInfo['src']
	theJson['alert']['dst']['geoip'] = geoInfo['dst']

	# ---------- add @timestamp ----------
	# use alert.occurred for timestamp. It is different for IPS vs other alerts...
	# ips-event alert.occurred format: 2014-12-11T03:28:08Z
	# all other alert.occurred format: 2014-12-11 03:28:33+00
	if theJson['alert']['name'] == 'ips-event':
		timeFormat = '%Y-%m-%dT%H:%M:%SZ'
	else:
		timeFormat = '%Y-%m-%d %H:%M:%S+00'

	oc = datetime.strptime(theJson['alert']['occurred'],timeFormat)	
	# Append YYYY.MM.DD to indexname like Logstash
	esIndexStamped = esIndex + oc.strftime('-%Y.%m.%d')    
	# Put the formatted time into @timestamp
	theJson['@timestamp'] = oc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

	# ---------- Remove alert.explanation.os-changes ----------
	# TODO: figure out a way to incorporate this info.
	# Doing this is complicated. Will require creative
	# Elasticsearch mapping (template?). Need to gather more json examples.
	if ('os-changes' in theJson['alert']['explanation']):
		# DEV: save the os-changes field to file for later review
		with open('oschanges.json', 'a') as outfile:
			fileData = 'TIMESTAMP: ' + theJson['@timestamp'] + ' - ' + theJson['alert']['name'] + ' - ' + theJson['alert']['id']  + '\n' 
			fileData = fileData + json.dumps(theJson['alert']['explanation']['os-changes']) + '\n--------------------\n\n'
			outfile.write(fileData)
		del theJson['alert']['explanation']['os-changes']
		print("[os-changes] deleted")
		
	# ---------- write to Elasticsearch ----------
	try:
      	  	res = es.index(index=esIndexStamped, doc_type=theJson['alert']['name'], body=theJson)
       	except:
	  	logging.exception("\n-------------------------------------\nES POST ERROR\nJSON SENT: %s \n-------------------------------------\nTIME: %s\n", json.dumps(theJson),datetime.utcnow())

	# ---------- send email alerts ----------
	if sendAlerts is True:
		try:
			firestic_alert.sendAlert(theJson)
		except:
			logging.exception("\n-----------\nEMAIL ERROR\n--------- JSON: %s \n----------\nTIME: %s\n", json.dumps(theJson), datetime.utcnow())

def queryGeoip(alertInfo) :
	geoipInfo = {}
	
	if (alertInfo['type'] == 'ips-event') and (alertInfo['mode'] == 'server'):
		# ips-event mode is server so src = external, dest = internal
		geoipInfo['dst'] = getGeoipRecord(alertInfo['dstIp'],intGeoipDatabase,'city')
		if geoipInfo['dst'] is not None:
			geoipInfo['dst']['asn'] = localASN
			geoipInfo['dst']['hostname'] = getHostname(alertInfo['dstIp'])
		geoipInfo['src'] = getGeoipRecord(alertInfo['srcIp'],extGeoipDatabase,'city')
		if geoipInfo['src'] is not None:
			geoipInfo['src']['asn'] = getGeoipRecord(alertInfo['srcIp'],ASNGeoipDatabase,'asn')
			geoipInfo['src']['hostname'] = getHostname(alertInfo['srcIp'])
	else:
		# treat all others as src = internal, dest = external
		geoipInfo['dst'] = getGeoipRecord(alertInfo['dstIp'],extGeoipDatabase,'city')
		if geoipInfo['dst'] is not None:
			geoipInfo['dst']['asn'] = getGeoipRecord(alertInfo['dstIp'],ASNGeoipDatabase,'asn')
			geoipInfo['dst']['hostname'] = getHostname(alertInfo['dstIp'])
		geoipInfo['src'] = getGeoipRecord(alertInfo['srcIp'],intGeoipDatabase,'city')
		if geoipInfo['src'] is not None:
			geoipInfo['src']['asn'] = localASN
			geoipInfo['src']['hostname'] = getHostname(alertInfo['srcIp'])
	
	# add long,lat coordinate field...Kibana needs a field [long,lat] for "bettermap"
	if geoipInfo['dst'] is not None:
		geoipInfo['dst']['coordinates'] = [geoipInfo['dst']['longitude'],geoipInfo['dst']['latitude']]
	if geoipInfo['src'] is not None:
		geoipInfo['src']['coordinates'] = [geoipInfo['src']['longitude'],geoipInfo['src']['latitude']]
	
	return geoipInfo

def getHostname(ipaddress):
	try:
		lu = socket.gethostbyaddr(ipaddress)
		return lu[0]
	except:
		return None

def getGeoipRecord (ipAddress, database, queryType) : # queryType = asn or city
	gi = pygeoip.GeoIP(database)
	if queryType == 'city':
		return gi.record_by_addr(ipAddress)
	elif queryType =='asn':
		return gi.org_by_addr(ipAddress)
	else:
		return None

def main():
	server = HTTPServer((httpServerIP, httpServerPort), MyRequestHandler)
	print "\nStarting HTTP server...\n"
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		print "\n\nHTTP server stopped.\n"

if __name__ == "__main__":
	es = Elasticsearch()
	logging.basicConfig(level=logging.WARNING, filename=logFile, format='%(asctime)s - %(levelname)s - %(message)s')
	main()
