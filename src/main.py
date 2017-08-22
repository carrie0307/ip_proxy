# -*- coding: UTF-8 -*-
import ip
import time
import threading
'''
所有需要获取ip的地方，都从ip.available_IP_q来获取， 或者ip = get_IP()

实际使用时可以考虑，将获取ip的几个线程都调整为setDaemon(True)
'''

if __name__ == '__main__':
    ip.run_Getter()
    print '--------'
    time.sleep(30) # 这个时间很关键，确切说是从运行
    ip.ip_Verify()
    time.sleep(120)
    watcher = threading.Thread(target=ip.ip_watcher)
    watcher.setDaemon(True)
    watcher.start()
    '''
        其他要运行的函数
        在需要获取代理ip的地方， ip = get_IP()
    '''
