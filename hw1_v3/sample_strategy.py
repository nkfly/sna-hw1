import sys
import MyDiffusionModel
import random

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
		print(player_id)
	else :
		r, enemy_select_nodes = get_round_and_enemy_latestest_select_nodes(player_id,status_file)

		model = MyDiffusionModel.MyMultiPlayerLTModel()
		if r == 1:
			model.original_init(nodes_file, edges_file, player_num = 2)
		else:
			model.store('text.txt', edges_file, player_num = 2)
		model.select_nodes(enemy_select_nodes, player_id = 0)
		random_select_nodes = model.DegreediscountGreedy(model.get_copy_graph(),nodes_num_per_iter)
		#random_select_nodes = [random.randint(0, model.get_nodes_num()) for i in range(nodes_num_per_iter)]
		print(random_select_nodes, end='\n')
		model.select_nodes(random_select_nodes, player_id = 1)
		write_selected_nodes('selected_nodes.txt', random_select_nodes)

		model.propagate()
		model.export('text.txt')
		