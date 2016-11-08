data = open("uniprot-human.txt", "r")
query = open("in.txt", "r")
lookup = {}

def fillData():
	for line in data:
		q = line.split()
		if len(q) == 1:
			lookup[q[0]] = ""
		else:
			lookup[q[0]] = q[1]
		
def answerQueries():
	numFound = 0
	numQueries = 0
	for ask in query:
		ask = ask.strip()
		numQueries += 1
	
		if ask in lookup:
			numFound += 1
			#print ask, lookup[ask]
		else:
			if '-' in ask:
				isoform = ask.split('-')
				if len(isoform) != 2:
					pass
				else:
					try:
						int(isoform[1])
						ask = isoform[0]
					except:
						pass
			if ask in lookup:
				numFound += 1
			else:
				print ask, "Not found."
	print "Found " + str(numFound) + " matches out of " + str(numQueries) + '; ' + str(numQueries-numFound) + ' not found.'
	
fillData()
answerQueries()