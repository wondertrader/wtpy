from wtpy.apps import WtHotPicker, WtCacheMonExchg, WtCacheMonSS, WtMailNotifier
import datetime
import logging

logging.basicConfig(filename='hotsel.log', level=logging.INFO, filemode="w", 
    format='[%(asctime)s - %(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
# 设置日志打印格式
formatter = logging.Formatter(fmt="[%(asctime)s - %(levelname)s] %(message)s", datefmt='%m-%d %H:%M:%S')
console.setFormatter(formatter)
# 将定义好的console日志handler添加到root logger
logging.getLogger('').addHandler(console)

def rebuild_hot_rules():
    '''
    重构全部的主力合约切换规则
    '''
    # 从交易所官网拉取行情快照
    cacher = WtCacheMonExchg()  

    # 从datakit落地的行情快照直接读取
    # cacher = WtCacheMonSS("../storage/his/snapshot/")

    picker = WtHotPicker(hotFile="hots.json", secFile="seconds.json")
    picker.set_cacher(cacher)

    sDate = datetime.datetime.strptime("2019-01-01", '%Y-%m-%d')
    eDate = datetime.datetime.strptime("2021-08-21", '%Y-%m-%d') # 可以设置为None，None则自动设置为当前日期
    hotRules,secRules = picker.execute_rebuild(sDate, eDate, wait=True)
    print(hotRules)
    print(secRules)

def daily_hot_rules():
    '''
    增量更新主力合约切换规则
    '''
    # 从交易所官网拉取行情快照
    cacher = WtCacheMonExchg()  

    # 从datakit落地的行情快照直接读取
    # cacher = WtCacheMonSS("../storage/his/snapshot/")

    picker = WtHotPicker(hotFile="hots.json", secFile="seconds.json")
    picker.set_cacher(cacher)

    # notifier = WtMailNotifier(user="yourmailaddr", pwd="yourmailpwd", host="smtp.exmail.qq.com", port=465, isSSL=True)
    # notifier.add_receiver(name="receiver1", addr="receiver1@qq.com")
    # picker.set_mail_notifier(notifier)

    eDate = datetime.datetime.strptime("2016-03-01", '%Y-%m-%d') # 可以设置为None，None则自动设置为当前日期
    picker.execute_increment(eDate)

rebuild_hot_rules()
input("press enter key to exit\n")