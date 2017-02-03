from BeautifulSoup import BeautifulSoup
from sets import Set
import urllib,urllib2

data = open("../human_data/data.txt", "r")
hgnc_data = open("../hgnc_data/hgnc_symbol_ac.txt", "r")
hgnc_gene_data = open("../hgnc_data/hgnc_symbol_previous_synonym.txt", "r")
query = open("in.txt", "r")
results = open("results.txt", "w")
lookup = {}
hgnc_lookup = {}
hgnc_gene_map = {}
QUERIES = []
MAP = {}
ENSEMBL_NAME = {}
STATUS = {}
STATUS_MSG = {0 : 'In HGNC', 1 : 'Converted from UniProt to HGNC', 2 : 'Not in HGNC', 3 : 'Obsolete', 4 : 'Unassigned', 5 : 'Bad ID, does not exist'}
DONE = {}

def fillData():
    # gets data from ../human_data/data.txt and creates the lookup table
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
                
def fillHGNCData():
    firstLine = 1 # ignore header line
    for line in hgnc_data:
        line = line.strip()
        if firstLine == 1:
            firstLine = 0
            continue
        line = line.split()
        gene_name = line[0].strip()
        for i in range(1, len(line)):
            AC = line[i].strip(" ,;")
            if AC in hgnc_lookup:
                hgnc_lookup[AC].append(gene_name)
            else:
                hgnc_lookup[AC] = [gene_name]
    for line in hgnc_gene_data: #first assign all approved symbols
        line = line.strip().split()
        gene_name = line[0].strip()
        hgnc_gene_map[gene_name] = gene_name
    for line in hgnc_gene_data: #then assign the synonyms and previous symbols
        line = line.strip().split()
        gene_name = line[0].strip()
        for i in range(0, len(line)):
            alternate_name = line[i].strip(" ,;")
            if alternate_name not in hgnc_gene_map:
                hgnc_gene_map[alternate_name] = gene_name
            
def getHGNCName(gene):
    if gene in hgnc_gene_map:
        return hgnc_gene_map[gene]
    else:
        return -1
        
def queryUniProt(to, queryString):
    url = 'http://www.uniprot.org/uploadlists/'
    params = {
        'from':'ACC',
        'to': to,
        'format':'tab',
        'query': queryString
    }

    data = urllib.urlencode(params)
    request = urllib2.Request(url, data)
    contact = ""
    request.add_header('User-Agent', 'Python %s' % contact)
    response = urllib2.urlopen(request)
    page = response.read(200000).splitlines()
    return page
    
        
def answerQueries():
    numHGNC = 0
    numFound = 0
    numQueries = 0
    numFoundNotInHGNC = 0
    notFoundQuery = ''
    remain = []
    
    for ask in query:
        ask = ask.strip()
        QUERIES.append(ask)
        numQueries += 1
    
        if ask in hgnc_lookup:
            numFound += 1
            numHGNC += 1
            MAP[ask] = hgnc_lookup[ask]
            STATUS[ask] = STATUS_MSG[0]
        elif ask in lookup:
            numFound += 1
            STATUS[ask] = STATUS_MSG[2]
            MAP[ask] = lookup[ask]
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
            if ask_isoform in hgnc_lookup:
                numFound += 1
                numHGNC += 1
                MAP[ask] = hgnc_lookup[ask_isoform]
                STATUS[ask] = STATUS_MSG[0]
            elif ask_isoform in lookup:
                numFound += 1
                STATUS[ask] = STATUS_MSG[2]
                MAP[ask] = lookup[ask_isoform]
            else:
                notFoundQuery += ask+' '
                remain.append(ask)
    print 'Resolving problematic IDs...'
    
    # get ID to check if entries exist
    page = queryUniProt('ID', notFoundQuery)
    entries = []
    for entry in page:
        entry = entry.split('\t')
        if entry[0] != 'From':
            entries.append(entry[0])

    # get gene names
    page = queryUniProt('GENENAME', notFoundQuery)
    geneNames = {}
    for entry in page:
        entry = entry.split('\t')
        geneNames[entry[0]] = entry[1]
    
    numUnassigned = 0
    
    # get Ensembl IDs
    page = queryUniProt('ENSEMBL_ID', notFoundQuery)
    ensemblID = {}
    for entry in page:
        entry = entry.split('\t')
        ensemblID[entry[0]] = entry[1]
    
    print
    print 'Unassigned IDs (Ensembl ID given where possible):'
    for ID in entries:
        if ID in geneNames and ID != 'From':
            STATUS[ID] = STATUS_MSG[2]
            MAP[ID] = geneNames[ID]
            while ID in remain:
                numFound += 1
                remain.remove(ID)
        else:    
            if ID in ensemblID and ID != 'From':
                print ID + ' ' + ensemblID[ID]
                ENSEMBL_NAME[ID] = ensemblID[ID]
            else:
                print ID
            STATUS[ID] = STATUS_MSG[4]
            while ID in remain:
                numUnassigned += 1
                remain.remove(ID)
    
    numObsolete = 0
    print
    print 'Obsolete IDs (last existing gene name on UniProt given):'
    toRemove = []
    obsoleteSet = Set()
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
                                MAP[ID] = []
                                found = False
                                for line in correct_page:
                                    if line[0:2] == 'GN':
                                        arrayGN = line.split()
                                        if arrayGN[1].split('=')[0] == 'Name':
                                            obsoleteSet.add(ID + ' ' + arrayGN[1].split('=')[1])
                                            MAP[ID].append(arrayGN[1].split('=')[1])
                                            found = True
                                if found:
                                    numFound += 1
                                STATUS[ID] = STATUS_MSG[3]
                                break
                        except:
                            pass
                    
                    numObsolete += 1
                    toRemove.append(ID)
    for ID in toRemove:
        remain.remove(ID)
    for msg in obsoleteSet:
        print msg
        
    for ask in QUERIES:
        if ask in DONE:
            results.write(DONE[ask])
            continue
    
        if ask not in MAP:
            MAP[ask] = ''
        if ask not in STATUS:
            STATUS[ask] = STATUS_MSG[5]
            MAP[ask] = "incorrect_ID"
            
        if STATUS[ask] == STATUS_MSG[0]:
            if type(MAP[ask]) == type([]):
                MAP[ask].sort()
                STATUS[ask] = MAP[ask][0] + " is in HGNC."
            else:
                STATUS[ask] = MAP[ask] + " is in HGNC."    
        elif STATUS[ask] == STATUS_MSG[2]:
            STATUS[ask] = MAP[ask] + " HUGO gene name not available, UniProt gene name returned."
        elif STATUS[ask] == STATUS_MSG[3]:
            STATUS[ask] = ask + " is obsolete, gene name is retrieved from old versions of UniProt"
        elif STATUS[ask] == STATUS_MSG[4] and ask in ENSEMBL_NAME:
            STATUS[ask] = ask + " is unassigned; its Ensembl ID is provided as gene name."
            results.write(ask + '\t' + ENSEMBL_NAME[ask] + '\t' + STATUS[ask] + '\n')
            DONE[ask] = ask + '\t' + ENSEMBL_NAME[ask] + '\t' + STATUS[ask] + '\n'
            continue
        elif STATUS[ask] == STATUS_MSG[4]:
            STATUS[ask] = ask + " is unassigned, no Ensembl ID available."
            results.write(ask + '\t' + 'uncharacterized_protein' + '\t' + STATUS[ask] + '\n')
            DONE[ask] = ask + '\t' + 'uncharacterized_protein' + '\t' + STATUS[ask] + '\n'
            continue
            
        elif STATUS[ask] == STATUS_MSG[5]:
            STATUS[ask] = ask + " does not exist."    
            
        if type(MAP[ask]) == type([]):
            ans = ask + '\t'
            ans += MAP[ask][0]
            ans += '\t' + STATUS[ask]
            if len(MAP[ask]) > 1:
                ans += " First name in alphabetical order given, other names: "
                for i in range(1, len(MAP[ask])):
                    ans += MAP[ask][i] + ' '
            ans += '\n'
                
            results.write(ans)
            DONE[ask] = ans
        else:
            results.write(ask + '\t' + MAP[ask] + '\t' + STATUS[ask] + '\n')
            DONE[ask] = ask + '\t' + MAP[ask] + '\t' + STATUS[ask] + '\n'
        
    
    print
    print "Bad IDs (does not exist in UniProt):"
    remain = Set(remain)
    for ID in remain:
        print ID
        
    print
    print str(numFound) + ' found; among these, ' + str(numHGNC) + ' found on HGNC, ' + str(numFound-numHGNC-numFoundNotInHGNC) + ' converted from UniProt to HGNC, ' + str(numFoundNotInHGNC) + ' on Uniprot but not HGNC.'
    print str(numUnassigned) + ' unassigned, ' + str(numObsolete) + ' obsolete, ' + str(numQueries-numFound-numUnassigned) + ' bad; ' + str(numQueries) + ' queries total.'
    print "Results written to results.txt."    
    
fillHGNCData()
fillData()
answerQueries()    