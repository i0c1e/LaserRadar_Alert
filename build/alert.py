# -*- coding:utf-8 -*-
from ctypes import *
import numpy as np
from datetime import datetime
import time, datetime
import json
import logging
import sqlite3
import configparser
import os


class ModelArgs:
    def __init__(self):
        # self.__conn = sqlite3.connect("args.db")
        # self.__cursor = self.__conn.cursor()
        # logging.info("Connect DB successfully.")
        pass
    # 读取参数配置信息
    def get_matrix_size(self) -> list:
        pass

    def get_threshold(self) -> list:
        pass

    def save_args(self) -> bool:
        self.__conn.execute("")
        self.__conn.commit()

    def close_db(self):
        # self.__conn.close()
        # logging.info("DB closed.")
        pass

class Sensor:
    def __init__(self):
        self.__curdir = os.path.dirname(os.path.abspath(__file__))

        self.__conf = configparser.ConfigParser()
        self.__conf.read(os.path.join(self.__curdir, "config.ini"))
        so_name = self.__conf.get("radar", "lib_name")
        # so_file = os.path.realpath(so_name)
        # print(os.path.join(self.__curdir, so_name))
        so_file = os.path.join(self.__curdir, so_name)

        self.__lib = CDLL(so_file)
        
        self.__args = ModelArgs()
        self.__matrix_size = self.__args.get_matrix_size()
        # self.__sensor_data = np.zeros([self.__matrix_size, self.__matrix_size])
        self.__threshold_data = self.__args.get_threshold()
        self.__target_shape = tuple(
            [self.__conf.getint("radar", "target_row"), self.__conf.getint("radar", "target_column")])

    def connect_device(self):
        rt = self.__lib.myConnectDevice()
        rt = True
        if not rt:
            logging.info("Device connect failed. error code: ")
        logging.info("Device connect successfully.")

    def export_csv(self, matrix: np.ndarray, csv_name: str):
        now = datetime.datetime.now()
        csv_filename = now.strftime("%Y-%m-%d_%H:%M:%S")
        export_dir = os.path.abspath("./export")
        export_file = os.path.join(export_dir, csv_name + "_" + csv_filename + ".csv")
        np.savetxt(export_file, matrix, delimiter=",")
        logging.info("Export CSV File: %s", export_file)

    def single_capture(self, capture_time: int = 3):
        if self.__conf.has_option("radar", "capture_time"):
            capture_time = self.__conf.getint("radar", "capture_time")
        logging.info("Single Capture Time: %d s", capture_time)
        if self.__conf.has_option("radar", "export_origin_matrix"):
            is_export_origin_matrix = self.__conf.getboolean("radar", "export_origin_matrix")
        if self.__conf.has_option("radar", "export_conv_matrix"):
            is_export_conv_matrix = self.__conf.getboolean("radar", "export_conv_matrix")

        my_capture = self.__lib.myCapture
        my_capture.restype = POINTER(c_int * 9600)
        try:
            num = 0
            while True:
                num = num + 1
                print("Call times: ", num)
                ret = my_capture()
                origin_matrix = np.array(list(ret.contents)).reshape(160, 60)
                n = 0
                r, c = 0, 0
                conv_list = list()
                while r < 160:
                    while c < 60:
                        # print("Line: %-3d, data[%3d:%-3d, %3d:%-3d], Sum: %-9d" %(n, r, r+10, c, c+10, matrix[r:r+10, c:c+10].sum()) )
                        conv_list.append(origin_matrix[r:r + 10, c:c + 10].sum() / 100 / 1000)  # 1000mm
                        c = c + 10
                        n = n + 1
                    c = 0
                    r = r + 10
                # print(matrix)
                conv_matrix = np.array(conv_list).reshape(16, 6)
                # print(conv_matrix)

                # determine if block
                threshold_matrix = self.read_threshold_data()
                logging.debug("Conv_Matrix:\n%s" % (conv_matrix))
                alert_matrix = conv_matrix[conv_matrix-threshold_matrix < 0]
                logging.info("Alert_Point:%d" % alert_matrix.size)
                logging.info("Alert_Matrix:\n%s" % alert_matrix)

                if is_export_origin_matrix is True:
                    self.export_csv(origin_matrix / 1000, "OriginMatrix")
                if is_export_conv_matrix is True:
                    self.export_csv(conv_matrix, "ConvMatrix")
                time.sleep(capture_time)
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt Program closing...")
            logging.info("KeyboardInterrupt Program closing...")
            # self.lib.myDisConnectDevice()

        except Exception as ex:
            logging.error("Error! Detail message: %s" % ex)
            # self.lib.myDisConnectDevice()
        # finally:
        #     # disconnect device
        #     self.__lib.myDisConnectDevice()

    # 获取传感器数据信息
    def get_sensor_data(self):
        return self.__sensor_data

    # 图像卷积
    def conv(kernel_size: int):
        pass

    def read_threshold_data(self) -> np.ndarray:
        threshold_matrix = np.loadtxt(open("threshold.csv"), delimiter=",", skiprows=0)
        if threshold_matrix.shape != self.__target_shape:
            logging.error("Threshold Matrix Shape Doesn't Match! Target Shape: %s , Read Shape: %s" % (
            str(self.__target_shape), str(threshold_matrix.shape)))
            raise Exception()
        logging.info("Threshold Matrix Shape Import Successfully, SizeL %s" % str(threshold_matrix.shape))
        return threshold_matrix

    # 拥堵判断
    def is_block(self) -> bool:
        self.__threshold_data
        return False

    # 调用机器人清堵
    def call_robot(self):
        pass

    def close_model(self):
        rt = self.__lib.myDisConnectDevice()
        rt = True
        if not rt:
            logging.info("Device disconnect error")
        logging.info("Device disconnected")
        self.__args.close_db()


if __name__ == '__main__':
    # load library
    # lib = CDLL("./libConchCV.so")

    # connect device
    # lib.myConnectDevice()
    # get function from library

    logging.basicConfig(level=logging.DEBUG, filename="radar.log", filemode="a",
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    logging.basicConfig(level=logging.ERROR, filename="error.log", filemode="a",
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    # 1. 读取配置信息
    # model_args = ModelArgs()
    sensor = Sensor()
    # 2. 定时调用so库获取实时数据
    sensor.connect_device()
    sensor.single_capture()

    # 3. 卷积生成堵塞状态矩阵
    sensor.conv()
    # 4. 判断是否堵料
    flag = sensor.is_block()
    # 5. 调用机器人清堵
    if (not flag):
        sensor.call_robot()

    # 6.关闭模型
    sensor.close_model()
