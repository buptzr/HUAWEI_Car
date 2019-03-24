import numpy as np
import copy

def floyd(d):
    D=copy.deepcopy(d)

    lengthD = len(D)                    #邻接矩阵大小
    p = list(range(lengthD))
    P = []
    for i in range(lengthD):
        P.append(p)
    P = np.array(P)
    for k in range(lengthD):
        for i in range(lengthD):
            for j in range(lengthD):
                if(D[i][j] >D[i][k]+D[k][j]):         #两个顶点直接较小的间接路径替换较大的直接路径
                    P[i][j] = P[i][k]                 #记录新路径的前驱
                    D[i][j] = D[i][k]+D[k][j]
    #print('各个顶点的最短路径:')
    for i in range(lengthD):
        for j in range(lengthD):
            #print('v%d' % (i+1) + '--' + 'v%d' % (j+1) + '\t' + 'dist_min:' + '\t' + str(D[i][j]) + '\t' + 'path:'+'v%d'%(i+1),end='' )
            temp=P[i][j]
            while (temp!=j):
                #print('--'+'v%d'%(temp+1),end='')
                temp=P[temp][j]
            #print('--'+'v%d'%(j+1))
    #print('P矩阵:')
    #print(P[25][17])
    #print('D矩阵:')
    for i in D:
        #print(i)
        pass
    return D,P


#if __name__ == '__main__':

