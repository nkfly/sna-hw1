import sys
import MyDiffusionModel

def get_round_and_nodes(player_id,status_file):
	nodes_list = list()
	with open(filename, 'r') as f:
		line = f.readline()
		entry = line.strip().split()
		for e in entry:
			nodes_list.append(int(e))
	return nodes_list



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
		model = MyDiffusionModel.MyMultiPlayerLTModel()
		model.original_init(nodes_file, edges_file, player_num = 2)
		model.export('text.txt')