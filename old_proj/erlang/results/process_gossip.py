#!/usr/bin/env python

import os
import fileinput
import sys
import re

msgCount = 0
badMsg = 0
knowdonttell = 0
dontknow = 0

def process_file(path):
	"""This function processes the file!"""
	global msgCount
	global badMsg
	global knowdonttell
	global dontknow
	global knowandtell

	nodeset = {}

	fd = open(sys.argv[1],"r")
	file_lines = fd.readlines()
	fd.close()

	print(sys.argv[1])

	for line in file_lines:
		if re.search("Tells", line):
			msgCount += 1
		elif re.search("Told someone who knew", line):
			badMsg += 1
		elif re.search("KnowDontTell", line):
			knowdonttell += 1
		elif re.search("DontKnow", line):
			dontknow += 1

# --------------------------------------------------------------------------------
# --- Main Function ---
# --------------------------------------------------------------------------------

if len(sys.argv) != 2:
	print("Insufficient Arguments")
	sys.exit()

process_file(sys.argv[1])

print("Total Messages Sent: " + str(msgCount))
print("Messages sent to a node that knew: " + str(badMsg))
print("Nodes in state KnowDontTell: " + str(knowdonttell))
print("Nodes in state DontKnow: " + str(dontknow))
