import networkx as nx
import sys
import operator

'''
This code implements the multiplayer LT model.
'''


'''
self.g.node[n]['status'] = 'activated'/'inactivated'/'selected' means the status of node n 
self.g.node[n]['owner'] means the owner of node n
self.g.node[n]['threshold'] means the threshold of node n
self.g.edge[n1][n2]['influence'] means the influence of the direct edge from n1 to n2
'''

class MyMultiPlayerLTModel():
	def original_init(self, nodes_file, edges_file, player_num):
		self.player_num = player_num
		self.g = None
		self.read_graph(nodes_file, edges_file)
		self.inactivated_num = self.g.number_of_nodes()
		
		# store the activated nodes of each player in all rounds
		self.total_activated_nodes = [list() for i in range(0, self.player_num)]
		
		# store the activated nodes of each player in one round
		self.activated_nodes = None
		
		# to store the selected nodes (of all players) in one round
		self.selected_nodes = None

		self.init_round()

	def export(self, my_nodes_file):
		with open(my_nodes_file, 'w') as f:
			print(self.inactivated_num, end='\n', file=f)
			print(" ".join([str(n) for n in self.total_activated_nodes[0]] ), sep='\t', end='\n', file=f)
			print(" ".join([str(n) for n in self.total_activated_nodes[1]] ), sep='\t', end='\n', file=f)
			for n in self.g.nodes():
				print(n, self.g.node[n]['threshold'],self.g.node[n]['status'],self.g.node[n]['owner'],self.g.node[n]['energy'][0],self.g.node[n]['energy'][1],sep='\t',end='\n', file=f)

	def store(self, my_nodes_file, edges_file, player_num):
		self.player_num = player_num
		self.g = None
		self.store_graph(my_nodes_file, edges_file)
		self.activated_nodes = None
		# to store the selected nodes (of all players) in one round
		self.selected_nodes = None
		self.init_round()

	def store_graph(self, my_nodes_file, edges_file):
		self.g = nx.DiGraph()
		# read nodes file
		with open(my_nodes_file, 'r') as f:
			self.inactivated_num = int(f.readline().strip().split()[0])
			self.total_activated_nodes = [ [int(n) for n in f.readline().strip().split()]  ,  [int(n) for n in f.readline().strip().split()]]
			for line in f:
				entry = line.strip().split('\t')
				assert len(entry) == 6
				n = int(entry[0])
				t = float(entry[1])
				s = entry[2]
				o = entry[3]
				e = [float(entry[4]), float(entry[5])]
				self.g.add_node(n, threshold = t, status=s, owner=o, energy=e)
				
		# read edges file 
		self.read_edge(edges_file)

	def read_edge(self, edges_file):
		# read edges file 
		with open(edges_file, 'r') as f:
			line = f.readline().strip().split()
			assert line[1] == 'Directed' 
			f.readline() 
			for line in f:
				entry = line.strip().split(' ')
				assert len(entry) == 3
				n1 = int(entry[0])
				n2 = int(entry[1])
				if (self.g.has_node(n1) and self.g.has_node(n2)):
					inf = float(entry[2])
					self.g.add_edge(n1, n2, influence = inf)

	# read graph from file
	def read_graph(self,nodes_file, edges_file):
		self.g = nx.DiGraph()
		# read nodes file
		with open(nodes_file, 'r') as f:
			f.readline() # skip one line
			for line in f:
				entry = line.strip().split(' ')
				assert len(entry) == 2
				n = int(entry[0])
				t = float(entry[1])
				self.g.add_node(n, threshold = t, status='inactivated', 
						owner=None, energy=[0.0 for i in range(0, self.player_num)])
				
		# read edges file 
		self.read_edge(edges_file)


	# Let player select the nodes
	def select_nodes(self, nodes_list, player_id):
		if type(nodes_list) is not list:
			return None
		
		# since player could select invalid (status: selected/activated) nodes
		# we create a list to store the actual selected nodes
		actual_selected_nodes = list()
		for n in nodes_list:
			if not self.g.has_node(n):
				return None
			if self.g.node[n]['status'] == 'inactivated':
				self.g.node[n]['status'] = 'selected'
				self.g.node[n]['owner'] = player_id
				self.selected_nodes.append(n)
				actual_selected_nodes.append(n)
		
		# update inactivated_num		
		self.inactivated_num -= len(actual_selected_nodes)
		
		return actual_selected_nodes

	# initialize each round
	def init_round(self):
		self.selected_nodes = list()
		self.activated_nodes = [list() for i in range(0,self.player_num)]


	def simulate_select_nodes(self, copy_g, nodes_list, player_id):
		
		# since player could select invalid (status: selected/activated) nodes
		# we create a list to store the actual selected nodes
		for n in nodes_list:
			if copy_g.node[n]['status'] == 'inactivated':
				copy_g.node[n]['status'] = 'selected'
				copy_g.node[n]['owner'] = player_id


	def simulate_propagate(self, copy_g, selected_nodes, player_id):
		visiting_nodes_set = set(selected_nodes)
		affected_nodes = set()
		my_activated_node = 0
		while len(visiting_nodes_set) > 0:
			new_activated_nodes_set = set()
			# propagate the influence
			for n1 in visiting_nodes_set:
				owner = copy_g.node[n1]['owner']
				for n2 in copy_g.successors(n1):
					if copy_g.node[n2]['status'] == 'inactivated':
						if n2 not in affected_nodes:
							affected_nodes.add(n2)
						copy_g.node[n2]['energy'][owner] += copy_g.edge[n1][n2]['influence']
						if copy_g.node[n2]['energy'][owner] >= copy_g.node[n2]['threshold']:
							new_activated_nodes_set.add(n2)
			
			# determine the owner of the activated node
			for n in new_activated_nodes_set:
				copy_g.node[n]['owner'] = player_id
				copy_g.node[n]['status'] = 'activated'
				my_activated_node = my_activated_node + 1
			
			# update the nodes set to visit
			visiting_nodes_set = new_activated_nodes_set
		return my_activated_node, affected_nodes

	# propagate this round
	def propagate(self):
		visiting_nodes_set = set(self.selected_nodes)
		while len(visiting_nodes_set) > 0:
			new_activated_nodes_set = set()
			
			# propagate the influence
			for n1 in visiting_nodes_set:
				owner = self.g.node[n1]['owner']
				for n2 in self.g.successors(n1):
					if self.g.node[n2]['status'] == 'inactivated':
						self.g.node[n2]['energy'][owner] += self.g.edge[n1][n2]['influence']
						if self.g.node[n2]['energy'][owner] >= self.g.node[n2]['threshold']:
							new_activated_nodes_set.add(n2)
			
			# determine the owner of the activated node
			for n in new_activated_nodes_set:
				max_energy = -1.0
				for p in range(0, self.player_num):
					energy = self.g.node[n]['energy'][p]
					if energy >= max_energy:
						owner = p
						max_energy = energy

				self.g.node[n]['owner'] = owner
				self.g.node[n]['status'] = 'activated'
				self.activated_nodes[owner].append(n)
			
			# update inactivated_nodes_num
			self.inactivated_num -= len(new_activated_nodes_set)

			# update the nodes set to visit
			visiting_nodes_set = new_activated_nodes_set

		# update total_activated_nodes
		for i in range(0, self.player_num):
			self.total_activated_nodes[i].extend(self.activated_nodes[i])


	# get activated nodes of certain player in that round
	def get_nodes_num(self):
		return len(self.g.nodes())

	def get_activated_nodes(self, player_id):
		assert player_id < self.player_num
		return self.activated_nodes[player_id]

	# check whether there is inactivated node or not
	def no_nodes_left(self):
		return self.inactivated_num == 0

	# print the game result
	def print_result(self):
		print('----------Game Result----------', file=sys.stderr)
		print('player_id number_of_activated_nodes', file=sys.stderr)
		for player_id, nodes_list in enumerate(self.total_activated_nodes):
			print(player_id+1, len(nodes_list), sep='\t') 
		print('-------------------------------', file=sys.stderr)

	def remove_activated_nodes(self):
		for n in self.selected_nodes:
			self.g.remove_node(n)
		for n in self.activated_nodes[0]:
			self.g.remove_node(n)
		for n in self.activated_nodes[1]:
			self.g.remove_node(n)

	def keep_giant_component(self):
		giant_connected_component_size = 0
		giant_connected_component = None
		for g in nx.weakly_connected_components(self.g):
			if len(g) > giant_connected_component_size:
				giant_connected_component_size = len(g)
				giant_connected_component = g
		self.g = self.g.subgraph(giant_connected_component)

	# return a copy of graph
	def get_copy_graph(self):
		return self.g.copy()
	# implement by Me
	def DegreediscountGreedy(self, graph,simulate_activated_nodes,k):
		list=[]
		ddv={}
		tv={}
		ddv=graph.degree() # dictionary of all graph degree
		for n in graph.nodes():
			if graph.node[n]['status']!='inactivated':#發現無法成為 Seed 的點，尋找他的鄰居並把他家進去統計 TV 中
				del ddv[n]
				neighbor=graph.neighbors(n)
				for i in neighbor:
					if i not in tv:
						tv[i]=0
					tv[i]=tv[i]+1
		for (key,item) in tv.items():
			if key in ddv:
				ddv[key] = graph.degree(key) - 2 * tv[key] - ( graph.degree(key) - tv[key] ) * tv[key] #改變該點的權重
		for i in range(k):
			max_n = max(ddv.items(),key=operator.itemgetter(1))[0]
			list.append(max_n) #把我們想要的 seed 選進去
			del ddv[max_n]
			neighbor=graph.neighbors(max_n)
			for i in neighbor:
				if i not in tv:
					tv[i]=0
				tv[i]=tv[i]+1
				ddv[i] = graph.degree(i) - 2 * tv[i] - ( graph.degree(i) - tv[i] ) * tv[i]
		return list


	def reset(self,copy_g, select_nodes, affected_nodes, untouched_g):
		for n in select_nodes:
			copy_g.node[n]['status'] = 'inactivated'
			copy_g.node[n]['owner'] = None
		for n in affected_nodes:
			copy_g.node[n]['status'] = untouched_g.node[n]['status']
			copy_g.node[n]['owner'] = untouched_g.node[n]['owner']			
			copy_g.node[n]['threshold'] = untouched_g.node[n]['threshold']
			copy_g.node[n]['energy'][0] = untouched_g.node[n]['energy'][0]
			copy_g.node[n]['energy'][1] = untouched_g.node[n]['energy'][1]


	def heuristic_greedy_lazy(self, simulate_activated_nodes, copy_g,enemy_selected_nodes,num_of_nodes, player_id):
		
		return_nodes_list = list()
		self.simulate_select_nodes(copy_g, enemy_selected_nodes, 0)
		last_time_activated_node = 0
		untouched_g = copy_g.copy()
		while num_of_nodes > 0:
			candidate_list = list()
			for n1 in simulate_activated_nodes:
				try_set = list(return_nodes_list)
				try_set.append(n1)
				
				self.simulate_select_nodes(copy_g, try_set, 1)


				my_activated_node, affected_nodes = self.simulate_propagate(copy_g,try_set, player_id)

				self.reset(copy_g,try_set,affected_nodes,untouched_g)
				candidate_list.append((n1, my_activated_node ))


			candidate_list.sort(key = lambda x: x[1], reverse = True)

			simulate_activated_nodes.remove(candidate_list[0][0])
			return_nodes_list.append(candidate_list[0][0])
			last_time_activated_node = candidate_list[0][1]
			num_of_nodes = num_of_nodes - 1

			if num_of_nodes == 0:
				break


			i = 1
			max_index = 0
			max_value = 0
			while i < len(candidate_list) and i < 300:
				try_set = list(return_nodes_list)
				try_set.append(candidate_list[i][0])
				
				self.simulate_select_nodes(copy_g, try_set, 1)


				my_activated_node, affected_nodes = self.simulate_propagate(copy_g,try_set, player_id)

				if my_activated_node > max_value:
					max_value = my_activated_node
					max_index = i
				self.reset(copy_g,try_set,affected_nodes,untouched_g)
				i = i + 1

			simulate_activated_nodes.remove(candidate_list[max_index][0])
			return_nodes_list.append(candidate_list[max_index][0])
			last_time_activated_node = max_value
			num_of_nodes = num_of_nodes - 1
				
			
			print(return_nodes_list)
			print(last_time_activated_node)


		return return_nodes_list



	def heuristic_greedy(self, simulate_activated_nodes, copy_g,enemy_selected_nodes,num_of_nodes, player_id):
		
		return_nodes_list = list()
		self.simulate_select_nodes(copy_g, enemy_selected_nodes, 0)
		last_time_activated_node = 0
		untouched_g = copy_g.copy()
		for i in range(num_of_nodes):
			candidate_list = list()
			for n1 in simulate_activated_nodes:
				try_set = list(return_nodes_list)
				try_set.append(n1)
				
				self.simulate_select_nodes(copy_g, try_set, 1)


				my_activated_node, affected_nodes = self.simulate_propagate(copy_g,try_set, player_id)
				# for a_c in layer_to_activated_node_list:
				# 	if copy_g.node[a_c]['owner'] == 1:
				# 		my_activated_node = my_activated_node + 1

				self.reset(copy_g,try_set,affected_nodes,untouched_g)
				candidate_list.append((n1, my_activated_node ))


			candidate_list.sort(key = lambda x: x[1], reverse = False)

			simulate_activated_nodes.remove(candidate_list[0][0])
			return_nodes_list.append(candidate_list[0][0])
			last_time_activated_node = candidate_list[0][1]
			print(return_nodes_list)
			print(last_time_activated_node)


		return return_nodes_list

	def heuristic_max_weight(self, simulate_activated_nodes, num_of_nodes):
		candidate_list = list()

		for n1 in simulate_activated_nodes:
			# sum over all influence value of out-edges
			sum_of_out_influence = 0.0
			for n2 in self.g.successors(n1):
				if self.g.node[n2]['status'] == 'inactivated':
					sum_of_out_influence += self.g.edge[n1][n2]['influence']
			candidate_list.append((n1, sum_of_out_influence))

		candidate_list.sort(key = lambda x: x[1], reverse = True)

		# store the selected nodes into return_nodes_list 
		return_num = min(num_of_nodes, len(candidate_list))
		return_nodes_list = list()

		for i in range(0, return_num):
			return_nodes_list.append(candidate_list[i][0])

		return return_nodes_list
	def mix_heuristic(self, enemy_selected_nodes, simulate_activated_nodes,num_of_nodes):
		return_nodes_list=list()
		#first=self.heuristic_max_weight(simulate_activated_nodes,int(4))
		new_g = self.get_copy_graph()
		first=self.DegreediscountGreedy(new_g,simulate_activated_nodes, 3)
		true_first = list()
		for n in first:
			if n not in enemy_selected_nodes:
				simulate_activated_nodes.discard(n)
				num_of_nodes = num_of_nodes - 1
				true_first.append(n)
		#second = self.DegreediscountGreedy(new_g,simulate_activated_nodes, int(6))
		second = self.heuristic_max_weight(simulate_activated_nodes,num_of_nodes)
		for n in true_first:
			return_nodes_list.append(n)
		for n in second:
			return_nodes_list.append(n)
		return return_nodes_list
		
	def get_graph_nodes(self):
		return self.g.nodes()
	def get_selected_nodes(self):
		return self.selected_nodes


	# def heuristic_greedy_c2(self, simulate_activated_nodes, copy_g,enemy_selected_nodes,num_of_nodes):
		
	# 	return_nodes_list = list()
	# 	self.simulate_select_nodes(copy_g, enemy_selected_nodes, 0)
	# 	for i in range(int(num_of_nodes/2)):
	# 		candidate_list = list()
	# 		for n1 in simulate_activated_nodes:
	# 			for n2 in simulate_activated_nodes:
	# 				if n2 < n1:
	# 					continue

	# 				try_set = list(return_nodes_list)
	# 				try_set.append(n1)
	# 				try_set.append(n2)
					
	# 				self.simulate_select_nodes(copy_g, try_set, 1)

	# 				layer_to_activated_node_list, affected_nodes = self.simulate_propagate(copy_g,try_set)
	# 				my_activated_node = 0
	# 				for a_c in layer_to_activated_node_list:
	# 					if copy_g.node[a_c]['owner'] == 1:
	# 						my_activated_node = my_activated_node + 1

	# 				self.reset(copy_g,try_set,affected_nodes)
	# 				candidate_list.append(((n1,n2), my_activated_node ))

	# 		candidate_list.sort(key = lambda x: x[1], reverse = True)

	# 		simulate_activated_nodes.remove(candidate_list[0][0][0])
	# 		simulate_activated_nodes.remove(candidate_list[0][0][1])
	# 		return_nodes_list.append(candidate_list[0][0][0])
	# 		return_nodes_list.append(candidate_list[0][0][1])

	# 	return return_nodes_list
