import configparser
import os
import logging
import numpy as np
from alert import Sensor
from ctypes import *
conf = configparser.ConfigParser()
conf.read("config.ini")
so_name = conf.get("radar", "lib_name")
print(conf.has_option("radar","lib_name2"))
print(conf.get("radar","device_ip"))
print(os.path.dirname(os.path.realpath(so_name)))
print(os.path.join(os.path.dirname(os.path.realpath(so_name)), so_name))
so_file = os.path.realpath(so_name)
print(so_file)

logging.basicConfig(level=logging.DEBUG, filename="radar.log", filemode="a",
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

sensor = Sensor()
matrix = sensor.read_threshold_data()
# print(matrix.shape)

lib = CDLL("./libConchCV.so")
con = lib.myConnectDevice
# ip = POINTER(c_char * 14)
# con.argtype = ip
# con(conf.get("radar","device_ip"))
# con(ip(c_char(b"192.168.123.10")))
con(c_char_p(b"192.168.123.10"),c_int(12345))
lib.myDisConnectDevice()
def print_matrix(matrix):
    for row in matrix:
        for j in row:
            print("\033[1;41m%s\033[0m " % j,end="")
        print("")
    # print("\033[1;41m%s\033[0m" % (conv_matrix-threshold_matrix < 0))

a = np.arange(10).reshape(5,2)
print_matrix(a)