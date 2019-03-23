from gen_map import Graph_Map
from controller import controller
from floyd import *
crosspath = 'C:/Dev/华为比赛/source/naive/1-map-training-2/cross.txt'
roadpath = 'C:/Dev/华为比赛/source/naive/1-map-training-2/road.txt'
carpath = 'C:/Dev/华为比赛/source/naive/1-map-training-2/car.txt'
import time
import copy

if __name__ == "__main__":


    '''
    start = time.time()
    a = copy.deepcopy(map)
    for i in range(20):
        map.crosslist = copy.deepcopy(a.crosslist)
        #map.carlist = copy.deepcopy(a.carlist)
        map.roadlist = copy.deepcopy(a.roadlist)
    print(time.time()-start)
    '''
    map = Graph_Map(crosspath, roadpath, carpath)
    dis_matrix, path_matrix = floyd(map.matrix)
    print(path_matrix)
    control = controller(map,path_matrix)
    control.main()

