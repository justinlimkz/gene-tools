import urllib,urllib2

data = open("../human_data/data.txt", "r")
query = open("in.txt", "r")
lookup = {}

def fillData():
	gene_name = ""
	proteins = []
	for line in data:
		q = line.split()
		if line[0:2] == 'ID':
			proteins = []
			gene_name = None
		if line[0:2] == 'AC':
			for str in q:
				if str == 'AC':
					continue
				protID = str.strip(",;")
				proteins.append(protID)
		if line[0:2] == 'GN' and gene_name == None:
			gene_name = q[1].split("=")[1].strip(",;")
			for prot in proteins:
				lookup[prot] = gene_name
		
def answerQueries():
	numFound = 0
	numQueries = 0
	notFoundQuery = ''
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
				print ask
				notFoundQuery += ask+' '
	print "Found " + str(numFound) + " matches out of " + str(numQueries) + '; ' + str(numQueries-numFound) + ' not found.'
	
	print 'Resolving these...'
	url = 'http://www.uniprot.org/uploadlists/'
	params = {
		'from':'ACC',
		'to':'GENENAME',
		'format':'tab',
		'query': notFoundQuery
	}

	data = urllib.urlencode(params)
	request = urllib2.Request(url, data)
	contact = "" # Please set your email address here to help us debug in case of problems.
	request.add_header('User-Agent', 'Python %s' % contact)
	response = urllib2.urlopen(request)
	page = response.read(200000)
	print page
	
fillData()
answerQueries()
