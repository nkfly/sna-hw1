import networkx as nx
import random
seed = list()
graph=nx.DiGraph()
fd= open("partB_egofb_ic_edges.txt","r")
content = fd.readlines()
for a in content[2:]:
	nodes=a.split(' ')
	source=int(nodes[0])
	target=int(nodes[1])
	graph.add_node(source,active=0)
	graph.add_node(target,active=0)
	w=float(nodes[2])
	graph.add_edge(source,target,weight = w)
fd.close()
fd= open("partB_egofb_ic_seeds.txt","r")
content = fd.readlines()
for a in content[0:]:
	nodes=a.split(' ')
	for n in nodes:
		seed.append(n)
seed.pop()
fd.close()
#done constructing the graph
limit=10000
sum=0
count=0

for i in range(limit):
	count=count+1
	seed2=seed[:]
	for n in seed:
		graph.node[int(n)]['active']=1
	total=0
	while(len(seed2)>0):
		tmp=int(seed2.pop())
		neighbors= graph.neighbors(tmp)
		for tadd in neighbors:
			add=int(tadd)
			if graph.node[add]['active'] == 0:
				weight=graph.edge[tmp][add]['weight']
				c=random.random()
				if c<=weight:
					graph.node[add]['active'] = 1
					seed2.append(add)
					total=total+1
	sum+=total
	# done one round inactive all node
	for n in graph.nodes():
		if graph.node[int(n)]['active']==1:
			graph.node[int(n)]['active'] = 0
	#print str(count)+": "+str(total) 
print(str(float(sum)/float(limit))) # output 863.7872 after 10000 iterations