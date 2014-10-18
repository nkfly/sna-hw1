import networkx as nx
import operator

def DegreediscountGreedy(self,nodes,graph,k):
	list=[]
	candidate_list=[]
	for n in nodes:
		sum_of_out_influence = 0.0
		if graph.node[n]['status']=='inactivated':
			for out_edge in graph.out_edges(n, data=True):
                sum_of_out_influence += out_edge[2]['influence']
        candidate_list.append((n, sum_of_out_influence))
	candidate_list.sort(key = lambda x: x[1], reverse = True)
	# store the selected nodes into return_nodes_list 
    return_num = min(k, len(candidate_list))
    for i in range(0, return_num):
        return_nodes_list.append(candidate_list[i][0])
	return list