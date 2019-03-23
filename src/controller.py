from gen_map import *
import copy
from random import choice
import random
class controller:
    def __init__(self,map:Graph_Map, path_matrix):
        self.map = map
        self.carlist = self.map.carlist
        self.roadlist = map.roadlist
        self.crosslist = self.map.crosslist
        self.path_matrix = path_matrix


    def car_scheduler(self, car_id, cross_id, option):
        if car_id == 0:####异常情况
            return -1
        if (option == 1 or option ==2):
            return max([val for val in self.crosslist[cross_id].roads if val in self.crosslist[self.path_matrix[cross_id-1][self.carlist[car_id].des-1]+1].roads])
        elif (option ==3):
            best_road = max([val for val in self.crosslist[cross_id].roads if val in self.crosslist[self.path_matrix[cross_id-1][self.carlist[car_id].des-1]+1].roads])
            choice_road = []
            for road in self.crosslist[cross_id].roads:
                if (road!= -1 and road != best_road and road != self.carlist[car_id].road_id):
                    choice_road.append(road)
            if (len(choice_road)):
                return choice(choice_road)
            else:
                return -1
        else:
            return -1

    def get_biggest_car(self, road_id, direction):#给定road_id，获取这条路在direction方向上优先级最高的车的id
        #返回0说明这条路不存在或者路上没有要运动的车
        #print('进入找车函数')
        if road_id == -1:
            return 0
        road = self.roadlist[road_id]
        flag = [False]*road.channel
        for row in range(road.length):
            for ch in range(road.channel):
                #print(road.car_queue.shape,road_id,direction,row,ch)
                cur = road.car_queue[direction][row][ch]
                if cur != 0:
                    if flag[ch] == False:
                        flag[ch] = True
                    if self.carlist[cur].iswait == True:
                        return cur
            if not (False in flag):
                return 0
        return 0

    def passing_cross(self, road_id,cross_id,direction, car_id,next_road_id):#汽车通过路口，修改相关参数,返回1说明调度成功，返回-1说明调度失败
        #print('----------------------------------------------',road_id,cross_id,direction, car_id,next_road_id)
        #print('buzhou2',road_id,cross_id,direction, car_id,next_road_id)
        thiscar = self.carlist[car_id]
        thisroad = self.roadlist[road_id]
        nextroad = self.roadlist[next_road_id]
        thiscross = self.crosslist[cross_id]
        index = thiscross.roads.index(next_road_id)
        nextcross = self.crosslist[thiscross.neighbors[index]]
        next_direction = nextcross.directions[nextcross.roads.index(next_road_id)]#求下一个路方向这个地方要重写


        s1 = thiscar.pos###汽车在当前道路的行驶距离
        minv2 = min(nextroad.speed,thiscar.speed)#下一条路的限速
        s2 = max(0,minv2-s1)##能在第二条路上行驶的距离
        pre_chedao = thiscar.chedao#先保存车再路1上的车道，备用
        if s2 == 0:
            thiscar.iswait = False
            thisroad.car_queue[direction][thiscar.pos][thiscar.chedao] = 0  # 先清除路1上面的这辆车的信息
            self.map.delete += 1
            thisroad.car_queue[direction][0][thiscar.chedao] = car_id
            self.map.add += 1
            thiscar.pos = 0
            flag = 1#flag为1表示变成停止状态但是没有出这一条路
        elif thiscar.des == cross_id:#这辆车到达目的地，消失
            thisroad.car_queue[direction][thiscar.pos][thiscar.chedao] = 0  # 先清除路1上面的这辆车的信息
            self.map.arrived += 1 #地图中已经到达的目的地的车辆数加1
            self.map.on_road -= 1#地图上车数量减一
            self.map.delete += 1
            flag = 3#flag为3表示已经到达目的地
        else:
            flag = 0#flag为0表示完全没有移动，直接变为终止状态
            for i in range(nextroad.channel):
                row = nextroad.length-1
                while row >= 0 and nextroad.car_queue[next_direction][row][i] == 0:
                    row -= 1
                lastcar_id = nextroad.car_queue[next_direction][row][i]
                #print('row=',row)
                if row == -1:
                    thisroad.car_queue[direction][thiscar.pos][thiscar.chedao] = 0  # 先清除路1上面的这辆车的信息
                    self.map.delete += 1
                    thiscar.road_id = next_road_id  # 修改这辆车的当前所处道路
                    thiscar.pos = nextroad.length - s2  # 修改这辆车的当前所处位置
                    thiscar.chedao = i  # 修改这辆车的所处车道
                    nextroad.car_queue[next_direction][thiscar.pos][i] = car_id
                    self.map.add += 1
                    flag = 2#flag为2表示到达下一条路
                    break

                if self.carlist[lastcar_id].iswait == True:#路2的当前车道上最后一辆车是在等待状态
                    if nextroad.length-row > s2:#这辆车没有被路2上当前车道上的车挡住
                        #print('最后的是等待但是没挡住')
                        flag = 2#flag为2表示到达下一条路
                        thisroad.car_queue[direction][thiscar.pos][thiscar.chedao] = 0#先清除路1上面的这辆车的信息
                        self.map.delete += 1
                        thiscar.road_id = next_road_id #修改这辆车的当前所处道路
                        thiscar.pos = nextroad.length-s2#修改这辆车的当前所处位置
                        self.carlist[car_id].chedao = i#修改这辆车的所处车道
                        nextroad.car_queue[next_direction][thiscar.pos][i] = car_id
                        self.map.add += 1
                        pass
                    else:#这辆车被路2上当前车道上的车挡住了
                        flag = -1##flag为1表示仍然为等待状态
                    break  # 不用再去别的车道上找位置了，退出循环
                else:#路2的当前车道上最后一辆车是在停止状态
                    if row == nextroad.length-1:#路2的当前车道上最后一辆车是在最末尾，无空位可进，就去下一个车道找空位
                        #print('满了')
                        continue
                    else:#有空位，插进去
                        flag = 2#flag为2表示到达下一条路
                        thisroad.car_queue[direction][thiscar.pos][thiscar.chedao] = 0  # 先清除路1上面的这辆车的信息
                        thiscar.road_id = next_road_id  # 修改这辆车的当前所处道路
                        thiscar.pos = max(nextroad.length - s2,row+1)  # 修改这辆车的当前所处位置
                        self.carlist[car_id].chedao = i  # 修改这辆车的所处车道
                        nextroad.car_queue[next_direction][thiscar.pos][i] = car_id#草！！！！！！！！！！！！！！
                        break
        thiscar.iswait = True if flag == -1 else False#只有flag=-1的情况下，这辆车还需要等待
        if flag == 0:
            for row in range(thisroad.length):
                for col in range(thisroad.channel):
                    id = thisroad.car_queue[direction][row][col]
                    if id > 0:
                        self.carlist[id].iswait = False

        if flag > 0:
            if flag == 3 or flag == 2:
                front_waitstate = True
                front_carpos = -1
                start_index = 0
            else:
                front_waitstate = False
                front_carpos = 0
                start_index = 1
            for row in range(start_index,thisroad.length):
                car__id = thisroad.car_queue[direction][row][pre_chedao]
                if car__id == 0:
                    continue
                car = self.carlist[car__id]
                minv = min(car.speed, thisroad.speed)
                if car.pos - front_carpos <= minv:  # 如果会碰到障碍物（路口或者前车）
                    car.iswait = front_waitstate  # 设置车的状态
                else:  # 如果不碰到障碍物，能达到停止状态
                    car.iswait = False
                    thisroad.car_queue[direction][car.pos][pre_chedao] = 0  # 车之前的位置置零
                    car.pos -= minv
                    thisroad.car_queue[direction][car.pos][pre_chedao] = car__id  # 车现在的的位置置为车的id
                front_waitstate = car.iswait
                front_carpos = car.pos

        return -1 if flag == -1 else 1

    def adjust_channel(self,direction, road_id, channel):#把道路road_id的channel车道内的车尽量变为停止状态,对应任务书中调度规则的第一步

        front_waitstate = True
        front_carpos = -1  #######################################################
        thisroad = self.roadlist[road_id]
        '''
        if self.map.arrived >= 5000:
            print(np.sum(thisroad.car_queue))
        '''
        for row in range(thisroad.length):
            car_id = thisroad.car_queue[direction][row][channel]
            if car_id == 0:
                continue
            #print('buzhou1', direction, road_id, channel,car_id)
            thiscar = self.carlist[car_id]
            minv = min(thiscar.speed, thisroad.speed)
            if thiscar.pos - front_carpos <= minv :  # 如果会碰到障碍物（路口或者前车）
                thiscar.iswait = front_waitstate  # 设置车的状态
            else:  # 如果不碰到障碍物，能达到停止状态
                thiscar.iswait = False
                thisroad.car_queue[direction][thiscar.pos][channel] = 0#车之前的位置置零
                thiscar.pos -= minv
                thisroad.car_queue[direction][thiscar.pos][channel] = car_id#车现在的的位置置为车的id
            front_waitstate = thiscar.iswait
            front_carpos = thiscar.pos

    def move_once(self, cross_id):#此函数是执行路口cross_id的一次调度（只调度一辆车），返回0说明无需调度，返回1说明调度成功，返回-1说明调度失败
        thiscross = self.crosslist[cross_id]
        road_ids = thiscross.roads  # 提取出路口连接的道路,已经从小到大排序
        directions = thiscross.directions# 道路的方向
        for idx in range(4):#遍历四个方向的路
            road_id = road_ids[idx]
            biggest_car_id = self.get_biggest_car(road_id, directions[idx])
            if  biggest_car_id == 0 or directions[idx] ==-1:#当前道路不存在或者当前道路没有等待车辆，就跳过去
                continue

            my_next_road_id = self.car_scheduler(biggest_car_id,cross_id,2)
            order = road_ids.index(my_next_road_id)#获取要去的路的id在road_ids中的编号


            thisroad = self.roadlist[road_id]
            if order == (idx+2)%4:  # 如果车是直行就直接走
                #print('zhixing')
                return self.passing_cross(road_id, cross_id, directions[idx],biggest_car_id, my_next_road_id)
                pass
            elif order == (idx + 1) % 4:
                iid = (idx + 3) % 4
                chongtu_road_id = road_ids[iid]
                if self.car_scheduler(self.get_biggest_car(chongtu_road_id, directions[iid]),cross_id,2) !=my_next_road_id:  # 右边车道没有直行车辆，就可以左拐
                    #print('zuoguai')
                    return self.passing_cross(road_id, cross_id, directions[idx],biggest_car_id, my_next_road_id)
                    pass
            else:
                iid1 = (idx + 1) % 4
                iid2 = (idx + 2) % 4
                chongtu_road_id1 = road_ids[iid1]
                chongtu_road_id2 = road_ids[iid2]
                # 左边车道不直行，上面车道不左拐，就可以右拐
                if self.car_scheduler(self.get_biggest_car(chongtu_road_id1, directions[iid1]),cross_id,2) !=my_next_road_id and\
                        self.car_scheduler(self.get_biggest_car(chongtu_road_id2, directions[iid2]),cross_id,2) !=my_next_road_id:
                    #print('yougaui')
                    return self.passing_cross(road_id, cross_id, directions[idx],biggest_car_id, my_next_road_id)
                    pass
        return 0#########返回0说明当前路口没有等待车辆，返回-1说明这个路口优先级最高的车移动失败，返回1说明移动成功



    def go_to_road(self, cross_id):
        thiscross = self.crosslist[cross_id]
        if len(thiscross.grage) == 0:
            return -1
        start_car_id = thiscross.grage[-1]
        start_car = self.carlist[start_car_id]
        if start_car.planTime > self.map.current_time:
            return -1
        my_next_road_id = self.car_scheduler(start_car_id,cross_id,1)#获取准备启动的车辆的走向
        my_next_road = self.roadlist[my_next_road_id]
        s = min(start_car.speed, my_next_road.speed)
        if thiscross.directions[thiscross.roads.index(my_next_road_id)] != 0:  # 要去的道路的正反方向
            direction = 0
        elif my_next_road.isDuplex == 0:
            direction = -1
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        else:
            direction = 1
        #print(direction,my_next_road_id,cross_id,s,start_car_id)
        flag = -1
        for i in range(my_next_road.channel):
            row = my_next_road.length - 1
            while row >= 0 and my_next_road.car_queue[direction][row][i] == 0:
                row -= 1
            lastcar_id = my_next_road.car_queue[direction][row][i]
            if row == -1:
                start_car.road_id = my_next_road_id  # 修改这辆车的当前所处道路
                start_car.pos = my_next_road.length - s  # 修改这辆车的当前所处位置
                start_car.iswait = False  # 修改这辆车的等待状态
                start_car.chedao = i  # 修改这辆车的所处车道
                my_next_road.car_queue[direction][start_car.pos][i] = start_car_id
                flag = 1
                break

            if self.carlist[lastcar_id].iswait == True:  # 路2的当前车道上最后一辆车是在等待状态
                if my_next_road.length - row > s:  # 这辆车没有被路2上当前车道上的车挡住
                    start_car.road_id = my_next_road_id  # 修改这辆车的当前所处道路
                    start_car.pos = my_next_road.length - s  # 修改这辆车的当前所处位置
                    start_car.iswait = False#修改这辆车的等待状态
                    start_car.chedao = i  # 修改这辆车的所处车道
                    my_next_road.car_queue[direction][start_car.pos][i] = start_car_id
                    flag = 1
                    pass
                else:  # 这辆车被路2上当前车道上的车挡住了
                    return -1
                    pass
                break  # 不用再去别的车道上找位置了，退出循环
            else:  # 路2的当前车道上最后一辆车是在停止状态
                if row == my_next_road.length - 1:  # 路2的当前车道上最后一辆车是在最末尾，无空位可进，就去下一个车道找空位
                    continue
                else:  # 有空位，插进去
                    start_car.road_id = my_next_road_id  # 修改这辆车的当前所处道路
                    start_car.pos = max(my_next_road.length - s,row+1)  # 修改这辆车的当前所处位置
                    start_car.iswait = False#修改这辆车的等待状态
                    start_car.chedao = i  # 修改这辆车的所处车道
                    my_next_road.car_queue[direction][start_car.pos][i] = start_car_id
                    flag = 1
                    break
        if flag == 1:
            thiscross.grage.pop()
            self.map.car_stared += 1
            self.map.on_road += 1
        return flag




    def one_diaodu(self):#一个时间片调度
        for road_id in self.map.roadidlist:  ##第一步：给每一条路上的车标记状态和移动
            thisroad = self.roadlist[road_id]
            for direction in range(thisroad.isDuplex + 1):
                for channel in range(thisroad.channel):
                    self.adjust_channel(direction, road_id, channel)
        while True:  ##第二步：处理所有等待车辆
            waiting_crosses = []
            success = 0
            for cross_id in self.map.crossidlist:
                state = self.move_once(cross_id)
                while state == 1:
                    success += 1
                    state = self.move_once(cross_id)
                if state == -1:
                    waiting_crosses.append(cross_id)
            if success == 0:  # 说明这一轮对路口的遍历中，一次成功调度都没有，则说明整体调度结束
                if len(waiting_crosses) > 0:
                    print("存在死锁或者假死锁")
                    #######################
                    # 改变某个车的方向，解除死锁
                    #######################
                break
        self.map.current_time += 1
        return  waiting_crosses

    def main(self):
        while self.map.arrived < len(self.map.carlist):
            #print('current_time', self.map.current_time, 'arrived', self.map.arrived,'onroad',self.map.on_road,'started',self.map.car_stared)
            #print(self.map.arrived)
            waiting_crosses = self.one_diaodu()
            #print(waiting_crosses)
            if self.map.on_road >= 20:
                continue
            nums = 0
            for cross_id in list(set(self.map.crossidlist)-set(waiting_crosses)):
                #print(self.crosslist[cross_id].grage)
                state = self.go_to_road(cross_id)
                #print(cross_id, state)
                while state == 1:
                    nums += 1
                    #print('123')
                    #print(self.crosslist[cross_id].grage)
                    state = self.go_to_road(cross_id)
                if nums + self.map.on_road >= 30:
                    break
        print(self.map.current_time)
        print('completed!')




