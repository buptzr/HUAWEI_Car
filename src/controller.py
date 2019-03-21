from .gen_map import *
map = Graph_Map()
carlist = map.carlist
roadlist = map.roadlist
crosslist = map.crosslist

def get_driving_direction(road_id, direction):#给定road_id，获取这条路在direction方向上优先级最高的车的行驶方向和车的id
    #返回0,0说明这条路不存在或者路上没有要运动的车
    if road_id == -1:
        return 0,0
    road = roadlist[[road_id]]
    flag = [False]*road.channel
    for row in range(road.length):
        for ch in range(road.channel):
            cur = road.car_queue[direction][row][ch]
            if cur != 0:
                if flag[ch] == False:
                    flag[ch] = True
                if carlist[cur].iswait == True:
                    return carlist[cur].direction,cur
        if not False in flag:
            return 0,0
    return 0,0

def passing_cross(road_id,cross_id,direction, car_id,next_road_id):#汽车通过路口，修改相关参数,返回1说明调度成功，返回-1说明调度失败
    thiscar = carlist[car_id]
    thisroad = roadlist[road_id]
    nextroad = roadlist[next_road_id]
    next_direction = 0 if nextroad.begin == cross_id else 1
    s1 = thiscar.pos-1###汽车在当前道路的行驶距离
    minv2 = min(nextroad.speed,thiscar.speed)#下一条路的限速
    s2 = max(0,minv2-s1)##能在第二条路上行驶的距离
    pre_chedao = thiscar.chedao#先保存车再路1上的车道，备用
    if s2 == 0:
        carlist[car_id].iswait = False
        carlist[car_id].pos = 1
        flag = 1
    else:
        flag = 1
        for i in range(nextroad.channel):
            row = nextroad.length-1
            while row >= 0 and nextroad.car_queue[next_direction][-1][i] == 0:
                row += 1
            lastcar_id = nextroad.car_queue[next_direction][row][i]
            if carlist[lastcar_id].iswait == True:#路2的当前车道上最后一辆车是在等待状态
                if nextroad.length-1-row >= s2:#这辆车没有被路2上当前车道上的车挡住
                    flag = 2
                    thisroad.car_queue[direction][thiscar.pos][thiscar.chedao] = 0#先清除路1上面的这辆车的信息
                    carlist[car_id].road_id = next_road_id #修改这辆车的当前所处道路
                    carlist[car_id].pos = nextroad.length-s2#修改这辆车的当前所处位置
                    #carlist[car_id].iswait = False#修改这辆车的等待状态
                    carlist[car_id].chedao = i#修改这辆车的所处车道
                    pass
                else:#这辆车被路2上当前车道上的车挡住了
                    flag = -1
                    pass
                break  # 不用再去别的车道上找位置了，退出循环
            else:#路2的当前车道上最后一辆车是在停止状态
                if row == nextroad.length-1:#路2的当前车道上最后一辆车是在最末尾，无空位可进，就去下一个车道找空位
                    continue
                else:#有空位，插进去
                    flag = 2
                    thisroad.car_queue[direction][thiscar.pos][thiscar.chedao] = 0  # 先清除路1上面的这辆车的信息
                    carlist[car_id].road_id = next_road_id  # 修改这辆车的当前所处道路
                    carlist[car_id].pos = max(nextroad.length - s2,row+1)  # 修改这辆车的当前所处位置
                    #carlist[car_id].iswait = False  # 修改这辆车的等待状态
                    carlist[car_id].chedao = i  # 修改这辆车的所处车道
                    break
        carlist[car_id].iswait = True if flag == -1 else False#只有flag=-1的情况下，这辆车还需要等待

    if flag == -1:
        return -1
    if flag == 2:
        adjust_channel(direction,road_id,pre_chedao)
    return 1

    pass

def adjust_channel(direction, road_id, channel):#把道路road_id的channel车道内的车尽量变为停止状态,对应任务书中调度规则的第一步
    front_waitstate = True
    front_carpos = 0  #######################################################
    thisroad = roadlist[road_id]
    for row in range(thisroad.length):
        car_id = thisroad.car_queue[direction][row][channel]
        if car_id == 0:
            continue
        thiscar = carlist[car_id]
        minv = min(thiscar.speed, thisroad.speed)
        pre_pos = thiscar.pos
        if thiscar.pos - front_carpos <= minv :  # 如果会碰到障碍物（路口或者前车）
            thiscar.iswait = front_waitstate  # 设置车的状态
        else:  # 如果不碰到障碍物，能达到停止状态
            thiscar.iswait = False
            thiscar.pos -= minv
            thisroad.car_queue[direction][pre_pos-1][channel] = 0#车之前的位置置零
            thisroad.car_queue[direction][thiscar.pos][channel] = car_id#车现在的的位置置为车的id
        front_waitstate = thiscar.iswait
        front_carpos = thiscar.pos

def move_once(cross_id):#此函数是执行路口cross_id的一次调度（只调度一辆车），返回0说明无需调度，返回1说明调度成功，返回-1说明调度失败
    thiscross = crosslist[cross_id]
    road_ids = thiscross.roads  # 提取出路口连接的道路,已经从小到大排序
    directions = thiscross.directions# 道路的方向
    for idx in range(4):#遍历四个方向的路
        road_id = road_ids[idx]
        my_direction,car_id = get_driving_direction(road_id,directions[idx])
        if  my_direction == 0:#当前道路不存在或者当前道路没有等待车辆，就跳过去
            continue

        thisroad = roadlist[road_id]
        if my_direction == 1:  # 如果车是直行就直接走
            return passing_cross(road_id, cross_id, directions[idx],car_id, road_ids[(idx+2)%4])
            pass
        elif my_direction == 2:
            iid = (idx + 3) % 4
            chongtu_road_id = road_ids[iid]
            if get_driving_direction(chongtu_road_id, directions[iid]) != 1:  # 右边车道没有直行车辆，就可以左拐
                return passing_cross(road_id, cross_id, directions[idx],car_id, road_ids[(idx + 1) % 4])
                pass
        else:
            iid1 = (idx + 1) % len(road_ids)
            iid2 = (idx + 2) % len(road_ids)
            chongtu_road_id1 = road_ids[iid1]
            chongtu_road_id2 = road_ids[iid2]
            # 左边车道不直行，上面车道不左拐，就可以右拐
            if get_driving_direction(chongtu_road_id1, directions[iid1]) != 1 and get_driving_direction(
                    chongtu_road_id2, directions[iid2]) != 2:
                return passing_cross(road_id, cross_id, directions[idx],car_id, road_ids[(idx + 3) % 4])
                pass
    return 0#########返回0说明当前路口没有等待车辆，返回-1说明这个路口优先级最高的车移动失败，返回1说明移动成功

########################################################################################
########################################################################################
for road_id in roadlist:##第一步：给每一条路上的车标记状态和移动
    thisroad = roadlist[road_id]
    for direction in range(thisroad.isDuplex+1):
        for channel in range(thisroad.channel):
            adjust_channel(direction,road_id,channel)


while True:##第二步：处理所有等待车辆
    success = 0
    error = 0
    for cross_id in map.crosslist:
        state = move_once(cross_id)
        while state == 1:
            success += 1
            state = move_once(cross_id)
        if state == -1:
            error += 1
    if sum == 0:#说明这一轮对路口的遍历中，一次成功调度都没有，则说明整体调度结束
        if error > 0:
            print("存在死锁或者假死锁")
        break