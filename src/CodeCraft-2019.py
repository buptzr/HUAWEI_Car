import logging
import sys
from gen_map import *
from floyd import *
from controller import *
import os
#logging.basicConfig(level=logging.DEBUG,
#                    filename='../logs/CodeCraft-2019.log',
#                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
#                    datefmt='%Y-%m-%d %H:%M:%S',
#                    filemode='a')

def data_output(m,P):
    result = ""
    for car_id in m.caridlist:
        res = '('+str(car_id)+','+str(m.carlist[car_id].planTime)
        i = m.carlist[car_id].start - 1
        j = m.carlist[car_id].dex - 1
        start_cross = i+1
        temp = P[i][j]
        path = []
        #print('path:' + 'v%d' % (i + 1), end='')
        while (temp != j):
            end_cross = temp + 1
            #print('--'+'v%d'%(temp+1),end='')
            tmp = [val for val in m.crosslist[start_cross].roads if val in m.crosslist[end_cross].roads]
            path.append(max(tmp))
            start_cross = end_cross
            temp = P[temp][j]
        #print('--' + 'v%d' % (j + 1))
        end_cross = temp + 1
        tmp = [val for val in m.crosslist[start_cross].roads if val in m.crosslist[end_cross].roads]
        path.append(max(tmp))
        for s in path:
            res += ',' + str(s)
        res +=')'
        result+= res+'\n'
        #print(path)

    return result

def main():
    if len(sys.argv) != 5:
        logging.info('please input args: car_path, road_path, cross_path, answerPath')
        exit(1)

    car_path = sys.argv[1]
    road_path = sys.argv[2]
    cross_path = sys.argv[3]
    answer_path = sys.argv[4]

    #logging.info("car_path is %s" % (car_path))
    #logging.info("road_path is %s" % (road_path))
    #logging.info("cross_path is %s" % (cross_path))
    #logging.info("answer_path is %s" % (answer_path))

    #graph_map = Graph_Map('../config/cross.txt', '../config/road.txt', '../config/car.txt')
    graph_map = Graph_Map(cross_path, road_path, car_path)
    dis_matrix, path_matrix = floyd(graph_map.matrix)


    #print(path_matrix)
    control = controller(graph_map, path_matrix)
    result = control.main()
    #print(result)
    f = open(answer_path,'w')
    f.write(result)
    f.close()

# to read input file
# process
# to write output file


if __name__ == "__main__":
    main()