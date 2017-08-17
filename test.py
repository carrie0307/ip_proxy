
# -*- coding: utf-8 -*-
# !/usr/bin/env python
class available_IP_usedup():
    def __init__(self):
        print "可用IP已用尽..."




if __name__ == '__main__':
    try:
        if 1<2:
            print 'ok'
            raise available_IP_usedup()
    except available_IP_usedup:
        print '---------------'
