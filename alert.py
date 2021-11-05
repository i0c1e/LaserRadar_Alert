# -*- coding:utf-8 -*-
from ctypes import *
import numpy as np
import cv2
from datetime import datetime
import time, datetime
import json
import logging
import sqlite3
import configparser
import matplotlib.pyplot as plt
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
        self.__open_flag = -1
        so_name = self.__conf.get("radar", "lib_name")
        # so_file = os.path.realpath(so_name)
        # print(os.path.join(self.__curdir, so_name))
        so_file = os.path.join(self.__curdir, so_name)

        self.__lib = CDLL(so_file)
        
        self.__args = ModelArgs()
        self.__matrix_size = self.__args.get_matrix_size()
        # self.__sensor_data = np.zeros([self.__matrix_size, self.__matrix_size])
        self.__device_ip = self.__conf.get("radar", "device_ip")
        
        # if self.__conf.has_option
        if self.__conf.has_option("radar", "port"):
            self.__port = self.__conf.getint("radar", "port")
        else:
            self.__port = 12345

        self.__threshold_data = self.__args.get_threshold()
        self.__target_shape = tuple(
            [self.__conf.getint("radar", "target_row"), self.__conf.getint("radar", "target_column")])

    def connect_device(self):
        rt = self.__lib.myConnectDevice(c_char_p(bytes(self.__device_ip,encoding="utf-8")),c_int(self.__port))
        logging.info("Device IP: %s" % self.__device_ip)
        rt = True
        if not rt:
            logging.error("Device connect failed. error code: ")
        logging.info("Device connect successfully.")
        self.__open_flag = 1

    def reconnect_device(self):
        logging.info("Device capture error, try reconnect device")
        self.close_model()
        time.sleep(5)
        self.connect_device()

    def export_csv(self, matrix: np.ndarray, csv_name: str):
        now = datetime.datetime.now()
        csv_filename = now.strftime("%Y-%m-%d_%H:%M:%S")
        export_dir = os.path.abspath("./export")
        export_file = os.path.join(export_dir, csv_name + "_" + csv_filename + ".csv")
        np.savetxt(export_file, matrix, delimiter=",")
        logging.info("Export CSV File: %s", export_file)

    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    def single_capture(self, capture_time: int = 3):
        if self.__conf.has_option("radar", "capture_time"):
            capture_time = self.__conf.getint("radar", "capture_time")
        logging.info("Single Capture Time: %d s", capture_time)
        if self.__conf.has_option("radar", "export_origin_matrix"):
            is_export_origin_matrix = self.__conf.getboolean("radar", "export_origin_matrix")
        if self.__conf.has_option("radar", "export_conv_matrix"):
            is_export_conv_matrix = self.__conf.getboolean("radar", "export_conv_matrix")

        my_capture = self.__lib.myCapture
        matrix_pointer = POINTER(c_float * 9600)
        # lista = (c_float * 9600)(np.zeros(9600).tolist())
        lista = (c_float * 9600)()
        my_capture.argtype = matrix_pointer
        my_capture.restype = c_int
        try:
            num = 0
            stepr = 5
            stepc = 5
            while True:
                num = num + 1
                print("Call times: ", num)

                rt_code = my_capture(lista)
                if(rt_code!=1):
                    self.reconnect_device()
                    continue
                return_matrix = lista
                # print(list(lista))
                # print(lista.contents)
                compute_matrix = [point for point in lista if point < 10000]
                logging.info("compute distance average: %.2f" % np.average(compute_matrix))
                logging.info("compute distance min: %.2f" % np.min(compute_matrix))

                # return_matrix = my_capture()
                # print("return_matrix type: %s, length: %s"%(type(return_matrix.contents), len(return_matrix.contents)))
                # if return_matrix._b_base_ is None:
                #     print("Return message is None, try reconnect.")
                # origin_matrix = np.array(list(return_matrix.contents)).reshape(160, 60)
                origin_matrix = np.array(list(return_matrix),dtype=np.float32).reshape(60, 160)

                tmp1_origin_matrix = np.r_[origin_matrix/400,origin_matrix/800]
                tmp2_origin_matrix = np.r_[origin_matrix/1000,origin_matrix/1500]
                #tmp3_origin_matrix = np.r_[origin_matrix/2500,origin_matrix/3000,origin_matrix/3500]
                #origin_matrix = np.c_[tmp1_origin_matrix,tmp2_origin_matrix,tmp3_origin_matrix]
                origin_matrix = np.c_[tmp1_origin_matrix,tmp2_origin_matrix]
                # origin_matrix = origin_matrix/2500

                # sigmoid
                origin_matrix = 1/(1+np.exp(-origin_matrix))
                # tanh
#                origin_matrix = (np.exp(origin_matrix)-np.exp(-origin_matrix))/(np.exp(origin_matrix)+np.exp(-origin_matrix))
                # plt.imshow(origin_matrix * 0.0038, cmap='gray_r')
                new_img = cv2.normalize(origin_matrix, origin_matrix, 0, 255, cv2.NORM_MINMAX)
                new_img = cv2.convertScaleAbs(new_img)
                # gray = cv2.cvtColor(new_img,cv2.COLOR_BGR2GRAY)
                cv2.namedWindow('radar', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                cv2.imshow("radar", new_img)
                cv2.waitKey(1)
                if cv2.waitKey(1) and 0xFF == ord('q'):
                    break
                # plt.imshow(new_img, cmap='gray')
                # plt.show()
                n = 0
                r, c = 0, 0
                conv_list = list()
                
                while r < 60:
                    while c < 160:
                        # print("Line: %-3d, data[%3d:%-3d, %3d:%-3d], Sum: %-9d" %(n, r, r+stepr, c, c+stepc, matrix[r:r+stepr, c:c+stepc].sum()) )
                        conv_list.append(origin_matrix[r:r + stepr, c:c + stepc].sum() / (stepr*stepc) / 1000)  # 1000mm
                        c = c + stepc
                        n = n + 1
                    c = 0
                    r = r + stepr
                # print(matrix)
                # conv_matrix = np.array(conv_list).reshape(16, 6)
                # conv_matrix = np.array(conv_list).reshape(40, 15)
                conv_matrix = np.array(conv_list).reshape(60//stepr, 160//stepc)
                # print(conv_matrix)

                # determine if block
                # threshold_matrix = self.read_threshold_data()
                threshold_matrix = np.ones(60//stepr * 160//stepc).reshape(60//stepr,160//stepc)

                # logging.debug("Conv_Matrix: %s" % (conv_matrix.shape))
                # logging.debug("Conv_Matrix: %s\n%s" % (conv_matrix.shape,conv_matrix))
                bool_matrix = conv_matrix-threshold_matrix > 0
                # self.print_matrix(bool_matrix)
                
                # logging.debug("Judge_Matrix:\n%s" % (conv_matrix-threshold_matrix < 0))
                alert_matrix = conv_matrix[conv_matrix-threshold_matrix < 0]
                # logging.info("Alert_Point:%d" % alert_matrix.size)
                # logging.info("Alert_Matrix:\n%s" % alert_matrix)

                if is_export_origin_matrix is True:
                    self.export_csv(origin_matrix / 1000, "OriginMatrix")
                if is_export_conv_matrix is True:
                    self.export_csv(conv_matrix, "ConvMatrix")
                time.sleep(capture_time)
                # time.sleep(1)
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt Program closing...")
            logging.info("KeyboardInterrupt Program closing...")
            # self.lib.myDisConnectDevice()

        except Exception as ex:
            logging.error("Error! Detail message: %s" % ex)
            # self.lib.myDisConnectDevice()
        finally:
        #     # disconnect device
            self.close_model()

    def print_matrix(self, matrix):
        # # 从左到右打印
        # matrix = np.transpose(matrix,[1,0])
        # matrix = matrix.reshape(60,160)
        for row in matrix:
            for j in row:
                if j == False:
                    # print("\033[1;41m%-7s\033[0m" % j,end="")
                    print("\033[1;41m  \033[0m" % j,end="")
                else:
                    # print("%-7s" % j,end="")
                    print("  ",end="")
            print("")
        # print("\033[1;41m%s\033[0m" % (conv_matrix-threshold_matrix < 0))
    
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
        logging.info("Threshold Matrix Shape Import Successfully, Size: %s" % str(threshold_matrix.shape))
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
        self.__open_flag = 0



if __name__ == '__main__':

    # 日志服务
    # Release
    # logging.basicConfig(level=logging.DEBUG, 
    #                      format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    logging.basicConfig(level=logging.DEBUG, filename="radar.log", filemode="a",
                         format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    # logging.basicConfig(level=logging.ERROR, filename="error.log", filemode="a",
    #                     format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    # Debug
    #logging.basicConfig(level=logging.DEBUG, filemode="a",format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


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
    if(sensor.__open_flag != 0):
        sensor.close_model()   
