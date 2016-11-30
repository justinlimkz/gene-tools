from BeautifulSoup import BeautifulSoup
import urllib,urllib2

data = open("../human_data/data.txt", "r")
query = open("in.txt", "r")
results = open("results.txt", "w")
lookup = {}

def fillData():
	'''
	gets data from ../human_data/data.txt and creates the lookup table; avoids sending large queries to UniProt, which would take time.
	'''
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
		else:
			ask_isoform = ''
			if '-' in ask:
				isoform = ask.split('-')
				if len(isoform) != 2:
					pass
				else:
					try:
						int(isoform[1])
						ask_isoform = isoform[0]
					except:
						pass
			if ask_isoform in lookup:
				numFound += 1
				results.write(ask + '\t' + lookup[ask_isoform] + '\n')
			else:
				notFoundQuery += ask+' '
				remain.append(ask)
	print 'Resolving problematic IDs...'
	
	'''
	get ID to check if entries exist
	'''
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
	
	'''
	get gene names
	'''
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
	
	'''
	get Ensembl IDs
	'''
	params = {
		'from':'ACC',
		'to':'ENSEMBL_ID',
		'format':'tab',
		'query': notFoundQuery
	}
	data = urllib.urlencode(params)
	request = urllib2.Request(url, data)
	contact = ""
	request.add_header('User-Agent', 'Python %s' % contact)
	response = urllib2.urlopen(request)
	page = response.read(200000).splitlines()
	ensemblID = {}
	for entry in page:
		entry = entry.split('\t')
		ensemblID[entry[0]] = entry[1]
	
	print
	print 'Unassigned IDs (Ensembl ID given where possible):'
	for ID in entries:
		if ID in geneNames and ID != 'From':
			results.write(ID + '\t' + geneNames[ID] + '\n')
			numFound += 1
		else:	
			numUnassigned += 1
			if ID in ensemblID and ID != 'From':
				print ID + ' ' + ensemblID[ID]
			else:
				print ID
		remain.remove(ID)
	
	numObsolete = 0
	print
	print 'Obsolete IDs (last existing gene name on UniProt given):'
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
					history_site = "http://www.uniprot.org/uniprot/" + ID + "?version=*"
					history_data = urllib2.urlopen(history_site)
					soup = BeautifulSoup(history_data)
					for link in soup.findAll('a'):
						try:
							possible_site = link.get('href')
							possible_prefix = possible_site.split('=')
							match = './' + ID + '.txt?version'
							if possible_prefix[0] == match:
								correct_site = "http://www.uniprot.org/uniprot"+possible_site[1:]
								correct_data = urllib2.urlopen(correct_site)
								correct_page = correct_data.read(200000).splitlines()
								for line in correct_page:
									if line[0:2] == 'GN':
										arrayGN = line.split()
										print ID, arrayGN[1].split('=')[1]
										break
								break
						except:
							pass
					
					numObsolete += 1
					toRemove.append(ID)
	for ID in toRemove:
		remain.remove(ID)
	
	print
	print "Bad IDs (does not exist in UniProt):"
	for ID in remain:
		print ID
		
	print
	print str(numFound) + ' found, ' + str(numUnassigned) + ' unassigned, ' + str(numObsolete) + ' obsolete, ' + str(numQueries-numFound-numUnassigned-numObsolete) + ' bad; ' + str(numQueries) + ' queries total.'
	print "Results written to results.txt."	
	
fillData()
answerQueries()	
