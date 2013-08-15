#!/usr/bin/python

import argparse
import sys
import csv
import xml.etree.ElementTree as ET
import time

def date_conversion(unix_epoch):
	"""
	Given a Unix Epoch time it returns a XML validated time form in UTC.
	"""
	return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(unix_epoch)))

# I recommend reading the GPX 1.1 documentation in order to fully understand
# what's going on here
def add_data(gpxdatatree, datalist):
	"""
	This function takes as input an empty GPX data tree and adds data from
	a list of lists in the form 
	[[unix_epoch_with_milliseconds, latitude, longitude, ...],...]
	and inserts it inside the GPX tree.
	"""
	track = gpxdatatree.find("trk").find("trkseg")
	for row in datalist:
		if len(row) == 0:
			continue
		trackpoint = ET.Element("trkpt", attrib={"lat":row[1], "lon":row[2]})
		time = ET.Element("time")
		time.text = date_conversion(row[0][:-3])
		trackpoint.append(time)
		track.append(trackpoint)

parser = argparse.ArgumentParser()
# The standard way of managing input/output files, defaulting to STDIN/OUT
# when not given a filename
parser.add_argument("infile",
	help="The CSV file to be converted (defaults to STDIN)",
	default=sys.stdin, nargs="?", type=argparse.FileType('r'))
parser.add_argument("outfile",
	help="Where to output the resulting GPX file (defaults to STDOUT)",
	default=sys.stdout, nargs="?", type=argparse.FileType('w'))
parser.add_argument("-s", "--skip-first-line",
	help="Avoids parsing the first line, usually containing the headers",
	action="store_true")
args = parser.parse_args()

inputfile = args.infile
outputfile = args.outfile

reader = csv.reader(inputfile)

inputdata = list(reader) # We extract all data from the CSV list

# Pretty self explanatory
if args.skip_first_line:
	inputdata = inputdata[1:]

# The root of the GPX tree
gpxdata = ET.Element("gpx", attrib={"version":"1.1", "creator":"csv2gpx",
	"xmlns":"http://www.topografix.com/GPX/1/1", "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance",
	"xsi:schemaLocation":"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"})
gpxdata.append(ET.Element("trk"))
gpxdata.find("trk").append(ET.Element("trkseg"))

# We now insert the data into the XML tree
add_data(gpxdata, inputdata)

tree = ET.ElementTree(element=gpxdata)
tree.write(outputfile, encoding="unicode", xml_declaration=True)
