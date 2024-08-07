#!/usr/bin/python3
#Copyright Bail 2024
#getup 早起打卡
#2024.8.5-2024.8.8

VERSION = 'v1.0.1.1'
VERCODE = 3

import sys,os,time,argparse,random,json

def init():
    '''初始化程序'''
    if not os.path.exists(getpath('datadir')):
        os.makedirs(getpath('datadir'))
    if not os.path.exists(getpath('history')):
        with open(getpath('history'),'w') as file:
            json.dump([],file)
    for i in getpath('all'):
        open(i,'a').close()
def getarg():
    '''获取命令行参数'''
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s','--set-clock',
                       help='设置计划起床时间\n格式: 时:分')
    group.add_argument('--history',
                       action='store_true',
                       help='获取打卡历史')
    group.add_argument('--version',
                       action='store_true',
                       help='获取程序版本')
    arg = parser.parse_args()
    return arg
def getpath(name:str)->str|tuple[str]:
    '''获取路径
name(str):要访问的路径名称
返回值:路径或包含路径的元组'''
    datadir = os.path.expanduser('~/.config/getup/')
    match name: # 该语法需要Python3.10及以上的版本
        case 'all':
            return (getpath(i) for i in ('history','clock'))
        case 'datadir':
            return datadir
        case 'history':
            return os.path.join(datadir,'history.json')
        case 'clock':
            return os.path.join(datadir,'clock')
        case _:
            raise ValueError(f'无此路径: {name}')
def daystamp()->int:
    '''计算日期戳(当前日期距离1970.1.1经过的天数)
返回值:日期戳(int)'''
    return int(time.time()//86400)
def welcome():
    '''欢迎页'''
    print('早起打卡')
    version()
def getclock()->tuple[int]:
    '''获取设定的时间
返回值:设定的时间(tuple(hour,minute))'''
    with open(getpath('clock')) as file:
        h,m = map(int,file.read().split(':'))
    return (h,m)
def memnumber()->bool:
    '''唤醒神器：即时记忆
返回值:是否通过测试(bool)'''
    print('下面将会出示10个数字，请在出示完成之后填写这10个数字，以保证你完全清醒。')
    nums = ''.join((str(random.randint(0,9)) for _ in range(10)))
    for i in nums:
        print(i,end='\r')
        time.sleep(1)
    user_input = input('请填写刚才出示的10个数字 >')
    if user_input == nums:
        print('填写正确')
        return True
    else:
        print('填写错误')
        return False
def is_in_valid_time(clock:tuple[int])->bool:
    '''检查是否在有效的时间段内打卡
clock(tuple[int]):预设的时钟(时,分)
返回值:打卡有效性(bool)'''
    nowh,nowm = map(int,time.strftime('%H %M').split())
    h,m = clock
    if (nowh==h) and (nowm-m <= 2):
        return True
    else:
        return False
def readfile()->list[int]:
    '''读取历史数据
返回值: 历史数据(list[int])'''
    with open(getpath('history')) as file:
        data:list[int] = json.load(file)
    return data
def calculate_daka_days(data:list[int])->int:
    '''计算已连续打卡的天数
data(list[int]):历史数据，其中的整数为“日期戳”
返回值:连同当天连续打卡的天数(int)'''
    count = 0
    for i in range(len(data)):
        if (i!=0) and (data[i-1]+1!=data[i]):
            count = 1
        else:
            count += 1
    return count+1  # 连同当天
def da3ka3(days:int):
    '''打卡界面
days(int):已连续打卡的天数'''
    print(f'恭喜！你已连续早起打卡{days}天！')
def save(data:list[int]):
    '''保存打卡数据
data(list[int]):历史数据，不包括当天，存放日期戳'''
    data.append(daystamp())
    with open(getpath('history'),'w') as file:
        json.dump(data,file)
def getup():
    '''早起打卡'''
    welcome()
    if not memnumber(): # 未通过测试
        sys.exit(0)
    clock = getclock()
    if is_in_valid_time(clock):
        data = readfile()
        days = calculate_daka_days(data)
        da3ka3(days)
        save(data)
    else:
        print('抱歉，你的打卡已超出有效时间。明天再来吧！')
        sys.exit(0)
def setclock(clock_time:str):
    '''设置闹钟
clock_time(str):时钟时间'''
    # 取值检验
    if ':' not in clock_time:
        print('E: 时间格式错误: 无英文冒号')
        sys.exit(255)
    if len(clock_time.split(':')) != 2:
        print('E: 时间格式错误: 冒号个数错误')
        sys.exit(255)
    try:
        h,m = map(int,clock_time.split(':'))
    except ValueError:
        print('E: 时间格式错误: 检测到非整数值')
        sys.exit(255)
    else:
        if not ((0<=h<=23) and (0<=m<=59)):
            print('E: 时间格式错误: 有超出范围的取值')
            sys.exit(255)
    # 检验通过
    with open(getpath('clock'),'w') as file:
        file.write(clock_time)
def version():
    '''显示版本'''
    print('_'.join((VERSION,str(VERCODE))))
def history():
    '''打卡历史'''
    print('抱歉，功能暂未开放')
def main():
    init()
    arg = getarg()
    if arg.set_clock:
        clock_time = arg.set_clock
        setclock(clock_time)
        return 0
    elif arg.history:
        history()
        return 0
    elif arg.version:
        version()
        return 0
    else:
        getup()
    return 0

if __name__ == '__main__':
    sys.exit(main())
