import networkx as nx
import sys

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

	# return a copy of graph
	def get_copy_graph(self):
		return self.g.copy()
