import networkx as nx
import operator
import math
import sys
#construct the graph
seed = list()
graph=nx.DiGraph()
fd= open("partB_egofb_lt_nodes.txt","r")
content = fd.readlines()
for a in content[1:]:
	nodes=a.split(' ')
	num=int(nodes[0])
	weight=float(nodes[1])
	graph.add_node(num,w = weight,pressure=0,active=0)
fd.close()
fd= open("partB_egofb_lt_edges.txt","r")
content = fd.readlines()
for a in content[2:]:
	nodes=a.split(' ')
	source=int(nodes[0])
	target=int(nodes[1])
	w=float(nodes[2])
	graph.add_edge(source,target,weight = w)
fd.close()
fd= open("partB_egofb_lt_seeds.txt","r")
content = fd.readlines()
for a in content[0:]:
	nodes=a.split(' ')
	for n in nodes:
		seed.append(n)
seed.pop()
fd.close()
#done constructing the graph
total=0
for n in seed:
	a = int(n)
	graph.node[a]['active']=2
while(len(seed)>0):
	tmp=int(seed.pop())
	neighbors= graph.neighbors(tmp)
	for tadd in neighbors:
		add=int(tadd)
		if graph.node[add]['active'] == 0:
			weight=graph.edge[tmp][add]['weight']
			graph.node[add]['pressure']=graph.node[add]['pressure']+weight
			if float(graph.node[add]['pressure'])>=float(graph.node[add]['w']):
				graph.node[add]['active'] = 1
				seed.append(add)
				total=total+1
print(str(total))
				
for num in graph.nodes():
	if int(graph.node[num]['active']) == 1:
		sys.stdout.write(str(num)+" ")