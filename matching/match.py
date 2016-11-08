data = open("gn.txt", "r")
query = open("in.txt", "r")
compare = open("compare.txt", "r")
'''
"gn.txt" is the file after grepping all lines starting with GN
"in.txt" has a list of pairs of gene names to be compared
"compare.txt" has a two lists of genes, separated by a newline
'''

main = {} 
# main is dictionary of lists, main[gene] is list of Names where gene is a synonym of Name

def fillMain():
	name = ""
	for line in data:
		q = line.split()
		for str in q:
			if str == "GN" or str[0] == '{':
				continue
			check = str.split("=")
			if len(check) > 1:
				type = check[0]
				gene = check[1].strip(",;")
				if type == "Name":
					name = gene
			else:
				gene = check[0].strip(",;")
			if gene not in main:
				main[gene] = [name]
			elif name not in main[gene]:
				main[gene].append(name)

def answerQueries():
	for line in query:
		if line.strip() == '':
			continue
		q = line.split()
		intersect = list(set(main[q[0]]).intersection(main[q[1]]))
		if len(intersect) >= 1:
			print "Match: " + intersect[0]
		else:
			print "No match."
			
def multipleGenes(): 
	#check genes with multiple Names
	count = 0
	for gene in main:
		if len(main[gene]) > 1:
			if gene in main[gene] and len(main[gene]) == 2:
				continue
			count += 1
			print gene + ": ",
			for i in main[gene]:
				print i,
			print
	print str(count) + " genenames associated with more than one gene."
	
def toMain(a):
	# convert a list of gene names to their main names
	R = []
	for k in a:
		if k in main:
			R.append(main[k][0])
	return R
	
def compareLists():
	L = [[], []]
	list = 0
	for gene in compare:
		if gene.strip() == '':
			list += 1
			continue
		L[list].append(gene.upper().strip())
	R = [None]*2
	R[0] = toMain(L[0])
	R[1] = toMain(L[1])
	count = 0
	for gene in R[0]:
		if gene in R[1]:
			print gene
			count += 1
	print str(count) + " (human) genes in common."
	print "List 1: " + str(len(L[0])-len(R[0])) + ' out of ' + str(len(L[0])) + ' not found.' 
	print "List 2: " + str(len(L[1])-len(R[1])) + ' out of ' + str(len(L[1])) + ' not found.'
	
fillMain()
compareLists()
#multipleGenes()

'''
old code:

		if len(main[q[1]]) == 1:
			q[0], q[1] = q[1], q[0]
	
		if len(main[q[1]]) == 1:
			if main[q[0]][0] == main[q[1]][0]:
				print "Match, Name: " + main[q[0]][0]
			else:
				print "No match, Names: " + main[q[0]][0] + " " + main[q[1]][0]
		else:
			if main[q[0]][0] in main[q[1]]:
				print "Match, Name: " + main[q[0]][0]
			else:
				print "No match, Names: " + main[q[0]][0] + " " + main[q[1]][0] + " more."
		
'''
			
			