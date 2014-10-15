import networkx as nx
import operator
import math
filename="partA_hepth.txt"
def create_graph_from_file(filename):
	#open the file
	try:
		fd = open(filename,"r")
	except:
		print("Can't open the file"+filename)
	content=fd.readlines()
	if content[0].strip() == "Undirected":
		graph = nx.Graph(type="Undirected")
		for a in content[1:]:
			nodes=a.split(' ')
			first=int(nodes[0])
			second=int(nodes[1])
			graph.add_edge(first,second)
	#	print("The Undirected Graph here has "+str(uGraph.number_of_edges())+" edges and "+str(uGraph.number_of_nodes())+" vertex")
	elif content[0].strip()=="Directed":
		graph = nx.DiGraph(type="Directed")
		for a in content[1:]:
			nodes=a.split(' ')
			first=int(nodes[0])
			second=int(nodes[1])
			graph.add_edge(first,second)
	#close the file
	try:
		fd.close();
	except: 
		pass
	return graph

def get_graph_degree_sequence_list(graph,reversed=False):
	if graph.graph['type'] == 'Undirected':
		return sorted(graph.degree().values(),reverse=reversed,key = int )

def get_graph_degree_destribution(graph):
	if graph.graph['type'] == 'Undirected':
		degs={}
		seq_list=get_graph_degree_sequence_list(graph)
		for n in seq_list:
			if n not in degs:
				degs[n] = 0
			degs[n]+=1
		return degs

def calculate_alpha(graph,mini=-1):
	if graph.graph['type'] == 'Undirected':
		#distribution=get_graph_degree_destribution(graph)
		if min == -1:
			dmin=min(nx.degree(graph).values(), key = int) # ki 的最小值 ki 表示 deree 為 i 的點有幾個
		else:
			dmin=mini
		n=graph.number_of_nodes() #n 為有幾種 degree
		sigma=0
		for value in nx.degree(graph).values():
				sigma=sigma+math.log(value/dmin)
		sigma=1/sigma
		return 1+n*sigma
	else:
		#turn the graph into undirect graph first
		newG = graph.to_undirected()
		newG.graph['type'] = 'Undirected'
		tmp = calculate_alpha(newG)
		return tmp

def get_graph_closeness_distribution(graph):
	if graph.graph['type'] == 'Undirected':
		closeness_dist={}
		for n in graph.nodes():
			closeness = round(nx.closeness_centrality(graph,n,normalized=False),3)
			if closeness not in closeness_dist:
				closeness_dist[closeness] = 0
			closeness_dist[closeness]+=1
		return closeness_dist
	else:
		components = list(nx.weakly_connected_components(graph))
		giant_comp = components[0]
		for component in components:
			if len(component) > len(giant_comp):
				giant_comp = component
		newG=graph.subgraph(giant_comp)
		closeness_dist={}
		for n in newG.nodes():
			closeness = round(nx.closeness_centrality(newG,n,normalized=False),3)
			if closeness not in closeness_dist:
				closeness_dist[closeness] = 0
			closeness_dist[closeness]+=1
		return closeness_dist

def get_graph_betweenness_distribution(graph):
	if graph.graph['type'] == 'Undirected':
		between_dictionary = nx.betweenness_centrality(graph)
		my_dic={}
		for (key,value) in between_dictionary.items():
			tmp = round(value,3)
			if tmp not in my_dic:
				my_dic[tmp] = 0
			my_dic[tmp]+=1
		return my_dic
	else:
		components = list(nx.weakly_connected_components(graph))
		giant_comp = components[0]
		for component in components:
			if len(component) > len(giant_comp):
				giant_comp = component
		newG=graph.subgraph(giant_comp)
		between_dictionary = nx.betweenness_centrality(newG)
		my_dic={}
		for (key,value) in between_dictionary.items():
			tmp = round(value,3)
			if tmp not in my_dic:
				my_dic[tmp] = 0
			my_dic[tmp]+=1
		return my_dic

def get_average_shortest_path_length(graph):
	if graph.graph['type'] == 'Undirected':
		pass
	else:
		components = list(nx.weakly_connected_components(graph))
		giant_comp = components[0]
		for component in components:
			if len(component) > len(giant_comp):
				giant_comp = component
		sum=0
		for i in giant_comp:
			for j in giant_comp:
				if i != j :
					if nx.has_path(graph,i,j):
						sum+=nx.shortest_path_length(graph,source=i,target=j)
		sum=sum/((len(giant_comp))*(len(giant_comp)-1))
		return sum
				
myGraph=create_graph_from_file(filename)


#alpha1=calculate_alpha(myGraph)
#print(str(round(alpha1,3))) # output 1.3153338168753834 undirected min = 1
#print(str(alpha1)) # output 1.3898714832111871 directed min = 1

#print(nx.average_shortest_path_length(myGraph) #TAKES A lot of time  output 3.6925068496963913
#print(nx.number_weakly_connected_components(myGraph)) #143 components
#shortest= get_average_shortest_path_length(myGraph)
#print(str(shortest)) # TAKES really a lot of time output 

# start to calculate closeness distribution 
'''closeness1 = get_graph_closeness_distribution(myGraph)
for key in sorted(closeness1,key = float):
	print(str(key),end="\t")
print("")
for key in sorted(closeness1,key = float):
	print(str(closeness1[key]),end="\t")'''

# start to calculate betweenness centrality
'''bet_cen = get_graph_betweenness_distribution(myGraph)
for key in sorted(bet_cen,key = float):
	print(str(key),end="\t")
print("")
for key in sorted(bet_cen,key = float):
	print(str(bet_cen[key]),end="\t")
'''