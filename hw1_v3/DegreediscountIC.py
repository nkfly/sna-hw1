import networkx as nx
import operator
'''
第一次使用
先把 graph 的 degree 通通讀近來 建立 DDV 的 dictionary 給以後使用
以後可能會讀取寫好的檔案直接做 DDV 的計算這樣比較省時間
'''

def DegreediscountGreedy(graph,k):
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