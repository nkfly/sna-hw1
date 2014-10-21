import sys
import MyDiffusionModel
import random
import networkx as nx


# round is 1-based
def get_round_and_enemy_latestest_select_nodes(player_id,status_file):
	line_count = 0
	enemy_latest_select_nodes = list()
	with open(status_file, 'r') as f:
		for line in f:
			line_count = line_count + 1
			
			if (player_id == 1 and line_count % 4 == 2 ) or (player_id == 2 and line_count % 4 == 1):
				enemy_latest_select_nodes = [int(n) for n in line.strip().split()]
	if line_count % 4 == 0:
		return int(line_count/4)+1, enemy_latest_select_nodes
	else:
		return int((line_count-1)/4)+1, enemy_latest_select_nodes

def write_selected_nodes(filename, select_nodes):
	with open(filename, 'w') as f:
		print(" ".join([str(n) for n in select_nodes]),end='\n', file=f)


def get_giant_connected_component(copy_g):
	giant_connected_component_size = 0
	giant_connected_component = None
	for g in nx.weakly_connected_components(copy_g):
		if len(g) > giant_connected_component_size:
			giant_connected_component_size = len(g)
			giant_connected_component = g
	return set(giant_connected_component)


# main function 
if __name__ == '__main__':
	player_id = int(sys.argv[1])
	nodes_file = sys.argv[2]
	edges_file = sys.argv[3]
	status_file = sys.argv[4]
	nodes_num_per_iter = int(sys.argv[5])
	selected_nodes_file = sys.argv[6]
	time_limit_in_sec = sys.argv[7]
	if player_id == 1:
		propagate=True #判定是否是第一回
		try:
			r, enemy_select_nodes = get_round_and_enemy_latestest_select_nodes(player_id,status_file) #嘗試讀檔失敗表示是第一回
		except:
			propagate = False
		model1 = MyDiffusionModel.MyMultiPlayerLTModel()#把 model 叫起來
		if propagate == True and int(r)>2: #r!=1
			nodes_list=model1.read_nodes_from_file('first_time_select.txt')
			model1.store('text1.txt', edges_file, player_num = 2) #表示我們是 player1 要讀圖
			model1.select_nodes(nodes_list, player_id = 0)
			model1.select_nodes(enemy_select_nodes, player_id = 1) #這邊是圖裡面自訂的 player id = 1 表示 player 2
			model1.propagate()
			model1.remove_activated_nodes()
		elif r==1:#r==1
			model1.original_init(nodes_file, edges_file, player_num = 2) #第一次啟用
			enemy_select_nodes=list()
		else: #r=2
			nodes_list=model1.read_nodes_from_file('first_time_select.txt')
			model1.original_init(nodes_file, edges_file, player_num = 2) #表示我們是 player1 要讀圖
			model1.select_nodes(nodes_list, player_id = 0)
			model1.select_nodes(enemy_select_nodes, player_id = 1) #這邊是圖裡面自訂的 player id = 1 表示 player 2
			model1.propagate()
			model1.remove_activated_nodes()
		#maintain giant component
		copy_g = model1.get_copy_graph()
		giant_connected_component = get_giant_connected_component(copy_g)
		#strategy phase
		random_select_nodes = model1.mix_heuristic(enemy_select_nodes,giant_connected_component,nodes_num_per_iter)
		print(random_select_nodes,file=sys.stderr)
		#選完後寫檔案
		write_selected_nodes('selected_nodes.txt', random_select_nodes)
		#輸出至我們的檔案
		if propagate == True and int(r)!=1:
			model1.export('text1.txt',mode=True)
			write_selected_nodes('first_time_select.txt', random_select_nodes)
		else:
			write_selected_nodes('first_time_select.txt', random_select_nodes)
	else :
		r, enemy_select_nodes = get_round_and_enemy_latestest_select_nodes(player_id,status_file)

		model = MyDiffusionModel.MyMultiPlayerLTModel()
		if r == 1:
			model.original_init(nodes_file, edges_file, player_num = 2)
		else:
			model.store('text.txt', edges_file, player_num = 2)
		copy_g = model.get_copy_graph()
		giant_connected_component = get_giant_connected_component(copy_g)
		
		
		model.simulate_select_nodes(copy_g,enemy_select_nodes, player_id = 0)
		#model.select_nodes(enemy_select_nodes, player_id = 0)

		# switch algorithm
		my_activated_node, affected_nodes = model.simulate_propagate(copy_g,enemy_select_nodes,0)

		for n in enemy_select_nodes:
			giant_connected_component.discard(n)

		#print(len(all_layer_activated_nodes),all_layer_activated_nodes,sep='\t',end='\n')
		#all_layer_activated_nodes = set.union(layer_to_activated_node_list[0], layer_to_activated_node_list[1],layer_to_activated_node_list[2])

		#print(all_layer_activated_nodes, end='\n')
		#print(model.get_graph_nodes(), end='\n')
		#random_select_nodes = model.heuristic_max_weight(all_layer_activated_nodes,nodes_num_per_iter)

		if r == 1:
			random_select_nodes = model.heuristic_greedy_lazy(giant_connected_component, model.get_copy_graph(),enemy_select_nodes,nodes_num_per_iter,player_id-1)

		else : 
			random_select_nodes = model.mix_heuristic(enemy_select_nodes,giant_connected_component,nodes_num_per_iter)
		#random_select_nodes = model.mix_heuristic(all_layer_activated_nodes,nodes_num_per_iter)
		#random_select_nodes = model.DegreediscountGreedy(model.get_copy_graph(),nodes_num_per_iter)
		#random_select_nodes = [random.randint(0, model.get_nodes_num()) for i in range(nodes_num_per_iter)]

		# switch algorithm
		#print(random_select_nodes, end='\n',file=sys.stderr)
		model.select_nodes(enemy_select_nodes, player_id = 0)
		model.select_nodes(random_select_nodes, player_id = 1)
		write_selected_nodes('selected_nodes.txt', random_select_nodes)

		

		model.propagate()
		model.remove_activated_nodes()
		#model.keep_giant_component()
		model.export('text.txt')
		