# ! /usr/bin/env python
# -*- coding: utf-8 -*-

from gurobipy import *

def tdn(k,n,m):
    model = Model("twin-domination-number")
    # 変数
    # 頂点の追加
    V = [i for i in range(1, n+1)]
    # colorの追加
    K = [i for i in range(1, k+1)]
    # 辺の追加
    x = {}
    for (i, j) in m:
        x[i, j] = model.addVar(vtype="B")
    # # color:頂点iはj色
    # y = {}
    # for i in V:
    #     y[i] = model.addVar(lb=1, ub=k, vtype="C")
    model.update()
    
    # 制約
    # model.addConstr(x[1, 1] == 1)
    # 各頂点は1色
    for i in V:
        model.addConstr(quicksum( x[l, i] for l in K ) == 1)
    # 各頂点を別の色で塗っても高々n色(この式意味ある?)
    model.addConstr(quicksum( x[l, i] for l in K for i in V) <= n)
    # 任意の頂点vに対して、N^+[v](出近傍)に少なくとも1つのjが含まれる。
    for v in V:
        neighbor = {}
        neighbor = [u for u in V if m[v, u] == 1] + [v]
        neighbor = sorted(list(set(neighbor)))
        print "N^+[%d]: %s" %(v, neighbor)
        for l in K:
            model.addConstr(quicksum( x[l, j] for j in neighbor) >= 1)
    # 任意の頂点vに対して、N^-[v](入近傍)に少なくとも1つのjが含まれる。
    for u in V:
        neighbor = {}
        neighbor = [v for v in V if m[v, u] == 1] + [u]
        neighbor = sorted(list(set(neighbor)))
        print "N^-[%d]: %s" %(u, neighbor)
        for l in K:
            model.addConstr(quicksum( x[l, j] for j in neighbor) >= 1)
    # # noインスタンスのときに早くなるかも、
    # for u in V:
    #     model.addConstr(quicksum( m[u, v]  for v in V) + 1 >= k)
    #     model.addConstr(quicksum( m[v, u]  for v in V) + 1 >= k)
    # 目的関数
    # 色jが小さい値の方が要素数が多くなるように
    #model.setObjective(quicksum( l * x[l, i] for l in K for i in V), GRB.MINIMIZE)
    model.setObjective(0, GRB.MINIMIZE)
    
    model.update()
    model.__data = x
    return model

def read_instance(filename):
    with open(filename, 'r') as f:
        # k = int(f.readline())
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
    # #入力
    # # color
    # k = 2
    # #オーダーn
    # n = 4
    # #隣接行列m_{ij}
    # m = { (1,1):0, (1,2):0, (1,3):0, (1,4):1,
    #       (2,1):1, (2,2):0, (2,3):0, (2,4):0,
    #       (3,1):1, (3,2):1, (3,3):0, (3,4):1,
    #       (4,1):0, (4,2):1, (4,3):1, (4,4):0
    # }
    argvs = sys.argv
    argc = len(argvs)
    if(argc <= 1):
        print "Usage: # python %s filename" % argvs[0]
        quit()
    n, m = read_instance(argvs[1])
    print "k>>"
    k = input()
    if (n <= k):
        print "no : twin domination numberはオーダー以下"
        quit()
    for (i, j) in m:
        if((m[i,j] < 0) or (m[i,j]>1)):
            print "Error:input is multi graph"
            quit()
    model = tdn(k,n,m)
    model.Params.OutputFlag = 1 # silent mode
    model.optimize()
    if model.Status == GRB.OPTIMAL:
        print "Opt.value=", model.ObjVal
        x = model.__data
        print "yes"
        for j in range(1, n+1):
            for l in range(1, k+1):
                if (x[l, j].X > 0.5):
                    print ("v(%d):%d" % (j, l))
    else:
        model.Params.OutputFlag = 1
        print "no"
