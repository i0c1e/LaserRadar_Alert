# -*- coding:utf-8 -*-
from ctypes import *
import numpy as np
import argparse
import cv2
from datetime import datetime
import time, datetime
import json
import logging
import configparser
import os,sys
import socket
import _thread
import threading


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
        self.__visible = True
        self.__retry_count = 5
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
    
    def set_ip(self, ip):
        self.__device_ip = ip

    def connect_device(self):
        rt = self.__lib.myConnectDevice(c_char_p(bytes(self.__device_ip,encoding="utf-8")),c_int(self.__port))
        logging.info("Device IP: %s" % self.__device_ip)
        if not rt:
            logging.error("Device connect failed. error code: ")
        logging.info("Device connect successfully.")
        self.__open_flag = 1

    def reconnect_device(self):
        logging.info("Device capture error, try reconnect device")
        self.close_model()
        time.sleep(5)
        self.connect_device()

    def set_visible(self, is_visible):
        self.__visible = is_visible
    
    def get_visible(self) -> bool:
        return self.__visible


    def export_csv(self, matrix: np.ndarray, csv_name: str):
        now = datetime.datetime.now()
        csv_filename = now.strftime("%Y-%m-%d_%H:%M:%S")
        export_dir = os.path.abspath("./export")
        export_file = os.path.join(export_dir, csv_name + "_" + csv_filename + ".csv")
        np.savetxt(export_file, matrix, delimiter=",")
        logging.info("Export CSV File: %s", export_file)

    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    def roi_compute(self,img, matrix):
        regions = self.__conf["roi"]["positions"]
        regions = json.loads(regions)
        for region in regions:
            x = int(regions[region]["x"])
            y = int(regions[region]["y"])
            longth = int(regions[region]["longth"])
            height = int(regions[region]["height"])
            # 计算均值
            region_matrix = matrix[y:y+height,x:x+longth]
            region_matrix = [value for value in region_matrix.flatten() if value < 10000]
            
            average = int(np.sum(region_matrix) // len(region_matrix))
            

            logging.info("compute region %s average distance: %.2f" % (regions[region]["name"], average))
            if average > 100 and average < regions[region]["distance"]:
                logging.info("#################    BLOCK DETECTED!    #################")
                logging.info("Area: [ %s ] blocked, Position: %s, Average distance: %s." %(regions[region]["name"], (x,y),average))
                logging.info("Call Robot......")
                self.call_robot(regions[region]["name"], (x,y), time.time)
            # distance = 1
            # 画框
            img = cv2.rectangle(img,(x,y),(x+longth,y+height),(0, 0, 255), 1)
            img = cv2.putText(img, regions[region]["name"] + ":"  + str(regions[region]["distance"]) + ":" + str(average) , 
            (x+40,y+10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1, lineType=cv2.LINE_AA)
            # img = cv2.putText(img, regions[region]["name"] + str(regions[region]["distance"]) + ":" + str(1) , 
            # (0,60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, ( 255,0, 0), 1, lineType=cv2.LINE_AA)
        return img

    def init_logger(self) -> bool:
        if self.__conf.has_option("log", "logfile"):
            logfile = self.__conf.get("log", "logfile")
        else:
            logfile = "logs/basic-log.txt"

        logfile_pointer = c_char_p(bytes(logfile,encoding="utf-8"))

        return self.__lib.my_init_logger(logfile_pointer)


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
                compute_matrix = origin_matrix

                tmp1_origin_matrix = np.r_[origin_matrix/400,origin_matrix/800]
                tmp2_origin_matrix = np.r_[origin_matrix/1000,origin_matrix/1500]
                #tmp3_origin_matrix = np.r_[origin_matrix/2500,origin_matrix/3000,origin_matrix/3500]
                #origin_matrix = np.c_[tmp1_origin_matrix,tmp2_origin_matrix,tmp3_origin_matrix]
                # origin_matrix = np.c_[tmp1_origin_matrix,tmp2_origin_matrix]
                origin_matrix = origin_matrix/1000

                # sigmoid
                # origin_matrix = 1/(1+np.exp(-origin_matrix))
                origin_matrix = self.sigmoid(origin_matrix)
                # tanh
#                origin_matrix = (np.exp(origin_matrix)-np.exp(-origin_matrix))/(np.exp(origin_matrix)+np.exp(-origin_matrix))
                # plt.imshow(origin_matrix * 0.0038, cmap='gray_r')
                new_img = cv2.normalize(origin_matrix, origin_matrix, 0, 255, cv2.NORM_MINMAX)
                new_img = cv2.convertScaleAbs(new_img)
                # gray = cv2.cvtColor(new_img,cv2.COLOR_BGR2GRAY)

                if self.get_visible() == True:
                    cv2.namedWindow('radar', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
                # 画框
                if np.max(origin_matrix) != 0.0 and self.__conf.has_option("roi", "enable_roi"):
                    if self.__conf.getboolean("roi", "enable_roi"):
                        self.roi_compute(new_img, compute_matrix)

                # if enable_roi:
                #     self.__conf.get()
                # if self.__conf.has_option("roi", "export_conv_matrix"):
                #     is_export_conv_matrix = self.__conf.getboolean("radar", "export_conv_matrix")
                # cv2.rectangle(new_img,(55,40),(93,47),(0, 0, 255), 1)
                # new_img = cv2.putText(new_img, "PA", (60,40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, lineType=cv2.LINE_AA)

                if self.get_visible():
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
    
    def continue_capture(self, threadname):
        my_continue_capture = self.__lib.my_continue_capture
        # rt = continue_capture()
        count = 0
        while count < 5:
            
            rt = my_continue_capture()
            # print("capture rt: ",rt)
            # print("-----------       %s reconnect. retry count:%d          ---------------" % (time.strftime('%y-%m-%d %H:%M:%S',time.localtime()),count))
            logging.error("==========   reconnect. retry count:%d   ==========" % (count + 1))
            if (rt == 0):
                count += 1
                time.sleep(1)
                self.reconnect_device()
            count = 0
        # 结束程序
        print("==========   try capture exit...   ==========")
        logging.error("Try Capture Error, Exit...")
        os._exit(1)
        # sys.exit()

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
    def get_sensor_data(self, threadname):
        my_get_data = self.__lib.my_get_data

        time.sleep(1)
        lista = (c_float*9600)()

        tmp_average = -1
        tmp_min = -1
        retry_count = 0

        while(retry_count < 5):
            try:
                rt = my_get_data(lista)
                # print(lista[0:9600])
                if rt != 1:
                    logging.warn("capture data size error : %d" % rt)
                    retry_count += 1
                    logging.warn("Wait 3s... Retry times: %d" % retry_count)
                    time.sleep(5)
                    continue

                compute_matrix = [point for point in lista if point < 10000]
                logging.info("compute distance average: %.2f" % np.average(compute_matrix))
                logging.info("compute distance min: %.2f" % np.min(compute_matrix))

                if(np.average(compute_matrix) == tmp_average and np.min(compute_matrix) == tmp_min):
                    logging.warn("******** Data Not Update ********")
                    retry_count += 1
                    logging.warn("Wait 3s... Retry times: %d" % retry_count)
                    time.sleep(5)
                    continue

                tmp_average,tmp_min = np.average(compute_matrix),np.min(compute_matrix)
                retry_count = 0

                origin_matrix = np.array(lista,dtype=np.float32).reshape(60, 160)

                img_matrix = origin_matrix/1000

                # sigmoid
                img_matrix = 1/(1+np.exp(-img_matrix))

                new_img = cv2.normalize(img_matrix, img_matrix, 0, 255, cv2.NORM_MINMAX)
                new_img = cv2.convertScaleAbs(new_img)

                if self.get_visible() == True:
                    cv2.namedWindow('radar', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)

                #画框
                if np.max(img_matrix) != 0.0 and self.__conf.has_option("roi", "enable_roi"):
                    if self.__conf.getboolean("roi", "enable_roi"):
                        new_img = self.roi_compute(new_img, origin_matrix)

                # cv2.rectangle(new_img,(55,40),(93,47),(0, 0, 255), 1)
                # new_img = cv2.putText(new_img, "PA", (60,40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, lineType=cv2.LINE_AA)

                if self.get_visible():
                    cv2.imshow("radar", new_img)
                    cv2.waitKey(1)
                    if cv2.waitKey(1) and 0xFF == ord('q'):
                        # break
                        return
                time.sleep(1)
            except Exception as ex:
                logging.error("Compute Exception: %s" % ex)
                retry_count += 1
                time.sleep(3)
                continue
        logging.error("Stop get sensor data. Thread exit...")
        os._exit(1)

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
    def call_robot(self,region_name, position, calltime):
        logging.info("Clean Task Start......")

        HOST = '127.0.0.1'    # The remote host
        PORT = 7788              # The same port as used by the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'Hello, world')
            data = s.recv(1024)
        # print('Received', repr(data))

        time.sleep(30)
        logging.info("Clean Task Done, Programme Continue......")

    def close_model(self):
        rt = True
        rt = self.__lib.myDisConnectDevice()
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
    # logging.basicConfig(level=logging.DEBUG, filemode="a",format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    logging.info("=================   Program Start   =================")

    parser = argparse.ArgumentParser(description="Radar Arg Parser")
    parser.add_argument('--ip',type=str, help='radar ip addr')
    parser.add_argument('--command',action='store_true', help='show GUI image')
    args = parser.parse_args()


    # 1. 读取配置信息
    # model_args = ModelArgs()
    sensor = Sensor()

    if args.ip :
        sensor.set_ip(args.ip)

    if args.command:
        sensor.set_visible(False)
    
    # 2. 初始化logger
    sensor.init_logger()

    # 3. 定时调用so库获取实时数据
    sensor.connect_device()
    # sensor.single_capture()
    # sensor.continue_capture()

    # 启动多线程
    try:
        _thread.start_new_thread( sensor.continue_capture, ("Thread-1", ) )
        _thread.start_new_thread( sensor.get_sensor_data, ("Thread-2", ) )
        while 1:
            # time.sleep(5)
            # break
            pass
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt Program closing...")
        logging.info("KeyboardInterrupt Program closing...")
    except Exception as ex:
        logging.error("Error! 无法启动线程")
        logging.error("Error! Detail message: %s" % ex)
    finally:
        # 6.关闭模型
        sensor.close_model()
        logging.info("=================   Program exit   =================")
    
    # 4. 调用机器人清堵
    # if (not flag):
    #     sensor.call_robot()

