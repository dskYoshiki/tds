# ! /usr/bin/env python
# -*- coding: utf-8 -*-

from gurobipy import *
import networkx as nx
# graphの描画
# import pylab 

def tdn(k,n,m):
    model = Model("twin-domination-number")
    # 変数
    # 頂点の追加
    V = [i for i in range(1, n+1)]
    # 分割数の追加
    K = [i for i in range(1, k+1)]
    # x[l,j]:頂点lは部分集合jに含まれる
    x = {}
    for (l, j) in m:
        x[l, j] = model.addVar(vtype="B")
        model.update()
    
    # 制約
    # model.addConstr(x[1, 1] == 1)
    # 各頂点は1色
    for i in V:
        model.addConstr(quicksum( x[l, i] for l in K ) == 1)
    # 任意の頂点vに対して、N^+[v](出近傍)に少なくとも1つのjが含まれる
    for v in V:
        neighbor = {}
        neighbor = [u for u in V if m[v, u] == 1] + [v]
        neighbor = sorted(list(set(neighbor)))
        # print "N^+[%d]: %s" %(v, neighbor)
        for l in K:
            model.addConstr(quicksum( x[l, j] for j in neighbor) >= 1)
    # 任意の頂点vに対して、N^-[v](入近傍)に少なくとも1つのjが含まれる
    for u in V:
        neighbor = {}
        neighbor = [v for v in V if m[v, u] == 1] + [u]
        neighbor = sorted(list(set(neighbor)))
        # print "N^-[%d]: %s" %(u, neighbor)
        for l in K:
            model.addConstr(quicksum( x[l, j] for j in neighbor) >= 1)
    # 目的関数
    # jが小さい値の方が要素数が多くなるように
    model.setObjective(quicksum( l * x[l, i] for l in K for i in V), GRB.MINIMIZE)
    #model.setObjective(0, GRB.MINIMIZE)
    
    model.update()
    model.__data = x
    return model

def lineDigraph(n, temp): # L(multidigraph)を出力
    # multigraph
    V = range(1, n+1)
    G = nx.MultiDiGraph()
    G.add_nodes_from(V)
    for (i, j) in temp:
        if (temp[i, j] > 0):
            for k in range(0,temp[i, j]):
                G.add_edge(i, j)
    # LineDigraph of G
    L = nx.line_graph(G)
    #adjance matrix : L.edges() → m
    n = len(L.nodes())
    v = {}
    atai = 1
    for i in L.nodes():
        v[i] = atai
        atai += 1
    m={}
    for i in range(1, n+1):
        for j in range(1, n+1):
            m[i, j] = 0
    for (i,j) in L.edges():
        m[ v[i], v[j] ] = 1
    return n, m

def k_LineDigraph(k, n, m): # L^k(D)を生成
    l=0
    while l < k:
        if (n > 1000): # PCが固まるので1000頂点以上のときは終了
            print "order of L^%d(D) is too large" %(l+1)
            quit()
        n, m = lineDigraph(n, m)
        print "order of L^%d(D) is %d" %(l+1, n)
        l += 1
    if(i == j):
        if(m[i,j]>1):
            print "Error:LineDigraphは各頂点のroopが高々1"
            print "関数lineDigraph()が間違い"
            quit()
    return n, m

def deg_Digraph(n, m): # Digraphの最小次数
    deg = float("inf")
    for i in range(1, n+1):
        out_deg = 0
        in_deg = 0
        for j in range(1, n+1):
            if ((i != j) and (m[i, j] == 1)):
                out_deg += 1
            if ((i != j) and (m[j, i] == 1)):
                in_deg += 1
        if (deg > out_deg):
            deg = out_deg
        if (deg > in_deg):
            deg = in_deg
    return deg


            
def read_instance(filename):
    with open(filename, 'r') as f:
        n = int(f.readline())
        V = range(1, n+1)
        m = {}
        i = 0
        for line in f:
            l = 0
            i += 1
            items = line.split(' ')
            for j in V:
                m[i, j] = (int(items[l]))
                l += 1
    f.close()
    return n, m

if __name__ == "__main__":
    argvs = sys.argv
    argc = len(argvs)
    if(argc <= 1):
        print "Usage: # python %s filename" % argvs[0]
        quit()
    n, m = read_instance(argvs[1])
    print "k>>"
    k = input()
    for (i, j) in m:
        if(m[i,j] < 0):
            print "Error:adjacence matrix is minus"
            quit()
    print "order of D is %d" %n
    line = 1
    n, m = k_LineDigraph(line, n, m) # line回LineDigraphをとる
    for (i, j) in m:    
        if(m[i,j]>1):
            print "Error:input of tdn() is multi graph"
            quit()
    if (n <= k):
        print "no : twin domination number is less than order of G"
        quit()
    model = tdn(k,n,m) # d^*(D) <= k の判定
    #model.Params.OutputFlag = 1 # silent mode
    model.optimize()
    deg = int(deg_Digraph(n, m))
    print "deg(L^%d(D)) = %d" %(line, deg)
    if model.Status == GRB.OPTIMAL:
        print "Opt.value=", model.ObjVal
        x = model.__data
        print "yes"
        r = {}
        for j in range(1, n+1):
            for l in range(1, k+1):
                if (x[l, j].X > 0.5):
                    # print ("v(%d):%d" % (j, l))
                    r[j]  = l
        a = {}
        for i in range(1, k+1):
            a[i] = [j for j in r if r[j] == i]
            print "V_%d : %s"%(i, a[i])
    else:
        print "no"
