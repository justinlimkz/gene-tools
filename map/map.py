import urllib,urllib2

data = open("../human_data/data.txt", "r")
query = open("in.txt", "r")
results = open("results.txt", "w")
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
	remain = []
	
	for ask in query:
		ask = ask.strip()
		numQueries += 1
	
		if ask in lookup:
			numFound += 1
			results.write(ask + '\t' + lookup[ask] + '\n')
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
				results.write(ask + '\t' + lookup[ask] + '\n')
			else:
				notFoundQuery += ask+' '
				remain.append(ask)
	#print "Found " + str(numFound) + " matches out of " + str(numQueries) + '; ' + str(numQueries-numFound) + ' not found.'
	print 'Resolving problematic IDs...'
	
	#get ID to check if entries exist
	url = 'http://www.uniprot.org/uploadlists/'
	params = {
		'from':'ACC',
		'to':'ID',
		'format':'tab',
		'query': notFoundQuery
	}

	data = urllib.urlencode(params)
	request = urllib2.Request(url, data)
	contact = ""
	request.add_header('User-Agent', 'Python %s' % contact)
	response = urllib2.urlopen(request)
	page = response.read(200000).splitlines()
	entries = []
	for entry in page:
		entry = entry.split('\t')
		if entry[0] != 'From':
			entries.append(entry[0])
	
	#get gene names
	params = {
		'from':'ACC',
		'to':'GENENAME',
		'format':'tab',
		'query': notFoundQuery
	}

	data = urllib.urlencode(params)
	request = urllib2.Request(url, data)
	contact = ""
	request.add_header('User-Agent', 'Python %s' % contact)
	response = urllib2.urlopen(request)
	page = response.read(200000).splitlines()
	geneNames = {}
	for entry in page:
		entry = entry.split('\t')
		geneNames[entry[0]] = entry[1]
	
	numUnassigned = 0
	print 'Unassigned IDs:'
	#print found gene names
	for ID in entries:
		if ID in geneNames and ID != 'From':
			results.write(ID + '\t' + geneNames[ID] + '\n')
			numFound += 1
		else:
			print ID
			numUnassigned += 1
		remain.remove(ID)
			
	#print str(numFound) + ' found, ' + str(numUnassigned) + ' unassigned.'
	
	numObsolete = 0
	print 'Obsolete IDs:'
	toRemove = []
	for ID in remain:
		site = "http://www.uniprot.org/uniprot/?query=id:" + ID + "&sort=score&columns=id,version&format=tab"
		data = urllib2.urlopen(site)
		page = data.read(2000000).splitlines()
		data.close()
		for entry in page:
			entry = entry.split('\t')
			if entry[0] != 'Entry':
				if entry[0] != ID:
					print "Weird, check query for " + ID
					break
				if (len(entry) > 1 and entry[1].strip() == '') or len(entry) == 1:
						print ID
						numObsolete += 1
						toRemove.append(ID)
	for ID in toRemove:
		remain.remove(ID)
	
	#print str(numObsolete) + ' obsolete, ' + str(numQueries-numFound-numUnassigned-numObsolete) + ' remain.'
	print "Bad IDs (does not exist in UniProt):"
	for ID in remain:
		print ID
		
	print
	print str(numFound) + ' found, ' + str(numUnassigned) + ' unassigned, ' + str(numObsolete) + ' obsolete, ' + str(numQueries-numFound-numUnassigned-numObsolete) + ' bad; ' + str(numQueries) + ' queries total.'
	print "Results written to results.txt."	
	
fillData()
answerQueries()	
