//
// Created by Charles on 2021/10/20.
//
#include <iostream>
#include <cstdio>
#include "HPS3DUser_IF.h"

static HPS3D_MeasureData_t g_measureData;
static float matrix[9600];
static int min_margin = 0;
static int average_margin = 0;
static int max = 0;
static int min = 999999;

static bool PrintResultData(HPS3D_EventType_t type, HPS3D_MeasureData_t data)
{
    //    int num = 9600;

//    printf("*************  HPS3D_FULL_DEPTH_EVEN    ********************\n");
   printf("distance_average:%d\n", data.full_depth_data.distance_average);
//    if (data.full_depth_data.distance_average > max) {
//        max = data.full_depth_data.distance_average;
//    }
//    if (data.full_depth_data.distance_average < min) {
//        min = data.full_depth_data.distance_average;
//    }
//    printf("    margin:%d\n", max-min);
    printf("distance_min    :%d\n", data.full_depth_data.distance_min);
    // if (data.full_depth_data.distance_min > max) {
    //      max = data.full_depth_data.distance_min;
    // }
    // if (data.full_depth_data.distance_min < min) {
    //     min = data.full_depth_data.distance_min;
    // }
    // printf("    margin:%d\n", max-min);
   printf("saturation_count:%d\n", data.full_depth_data.saturation_count);

    //    FILE *distance = NULL;
    //    distance = fopen("/mnt/d/TechDev/test.txt", "w+");
    //    matrix = data.full_depth_data.distance;
    //    for (int i = 0; i < num; i++) {
    //        matrix[i] = data.full_depth_data.distance[i];
    //        std::cout << "The distance " << i+1 << ": " << data.full_depth_data.distance[i] << std::endl;
    //        std::cout << "The pointCloud " << i+1 << ": (" << data.full_depth_data.point_cloud_data.point_data[i].x << ", "
    //                  << data.full_depth_data.point_cloud_data.point_data[i].y << ", "
    //                  << data.full_depth_data.point_cloud_data.point_data[i].z << ")" << std::endl;

    //    }

    //    printf("==========================================================\n\n");

    return true;
}

static void EventCallBackFunc(int handle, int eventType, uint8_t *data, int dataLen, void *userPara)
{
    std::cout << "default callback" << std::endl;

    switch ((HPS3D_EventType_t)eventType)
    {
    case HPS3D_SIMPLE_ROI_EVEN:
    case HPS3D_FULL_ROI_EVEN:
    case HPS3D_FULL_DEPTH_EVEN:
    case HPS3D_SIMPLE_DEPTH_EVEN:
        //            std::cout << "Simple" << std::endl;
        HPS3D_ConvertToMeasureData(data, &g_measureData, (HPS3D_EventType_t)eventType);
        PrintResultData((HPS3D_EventType_t)eventType, g_measureData);
        break;
    case HPS3D_SYS_EXCEPTION_EVEN:
        printf("SYS ERR :%s\n", data);
        break;
    case HPS3D_DISCONNECT_EVEN:
        printf("Device disconnected!\n");
        HPS3D_CloseDevice(handle);
        break;
    case HPS3D_NULL_EVEN:
    default:
        std::cout << "default callback" << std::endl;
        break;
    }
}

static int g_handle = -1;

static HPS3D_StatusTypeDef connectDevice()
{
    HPS3D_StatusTypeDef ret = HPS3D_RET_OK;
    ret = HPS3D_EthernetConnectDevice((char *)"192.168.123.10", 12345, &g_handle);
    //    if (ret != HPS3D_RET_OK) {
    //        printf("connect failed,Err:%d\n", ret);
    //    }
    return ret;

    printf("Dev Ver:%s\n", HPS3D_GetDeviceVersion(g_handle));
    printf("SN:%s\n\n", HPS3D_GetSerialNumber(g_handle));
}

static HPS3D_StatusTypeDef connectDevice(char *ip_addr, int port)
{
    HPS3D_StatusTypeDef ret = HPS3D_RET_OK;
    std::cout << ip_addr << ":" << port << std::endl;
    ret = HPS3D_EthernetConnectDevice((char *)ip_addr, port, &g_handle);
    //    if (ret != HPS3D_RET_OK) {
    //        printf("connect failed,Err:%d\n", ret);
    //    }

    printf("Dev Ver:%s\n", HPS3D_GetDeviceVersion(g_handle));
    printf("SN:%s\n\n", HPS3D_GetSerialNumber(g_handle));
    return ret;
}

static void disConnectDevice()
{
    int isConect;

    HPS3D_StopCapture(g_handle);
    HPS3D_CloseDevice(g_handle);
    //    HPS3D_MeasureDataFree(&g_measureData);

    isConect = HPS3DAPI_IsConnect(g_handle);
    if (isConect != 1)
    {
        std::cout << "Device is disconnected" << std::endl;
    }
    else
    {
        std::cout << "Device is not disconnected" << std::endl;
    }
}

static int capture(float *return_matrix)
{
    static HPS3D_StatusTypeDef ret = HPS3D_RET_OK;
    static HPS3D_DeviceSettings_t settings;
    static HPS3D_EventType_t type = HPS3D_SIMPLE_DEPTH_EVEN;

    //初始化内存
    ret = HPS3D_MeasureDataInit(&g_measureData);
    if (ret != HPS3D_RET_OK)
    {
        printf("MeasureDataInit failed,Err:%d\n", ret);
        return HPS3D_RET_ERROR;
    }

    //register callback function
    //    ret = HPS3D_RegisterEventCallback(EventCallBackFunc, NULL);
    //    if (ret != HPS3D_RET_OK) {
    //        std::cout << "RegisterEventCallback err: " << ret << std::endl;
    ////        return HPS3D_RET_ERROR;
    //    }
    ret = HPS3D_ExportSettings(g_handle, &settings);

    if (ret != HPS3D_RET_OK)
    {
        std::cout << "导出设备参数失败,Err:" << ret << "\"" << std::endl;
        return HPS3D_RET_ERROR;
    }

    //    printf("分辨率为:%d X %d\n", settings.max_resolution_X, settings.max_resolution_Y);
    //    printf("支持最大ROI分组数量为:%d  当前ROI分组：%d\n", settings.max_roi_group_number, settings.cur_group_id);
    //    printf("支持最大ROI数量为:%d\n", settings.max_roi_number);
    //    printf("支持最大多机编号为:%d，当前设备多机编号:%d\n", settings.max_multiCamera_code, settings.cur_multiCamera_code);
    //    printf("当前设备用户ID为：%d\n", settings.user_id);
    //    printf("光路补偿是否开启: %d\n\n", settings.optical_path_calibration);

    //单次测量

    ret = HPS3D_SingleCapture(g_handle, &type, &g_measureData);
    if (ret != HPS3D_RET_OK)
    {
        printf("SingleCapture failed,Err:%d\n", ret);
        return HPS3D_RET_ERROR;
    }
    PrintResultData(type, g_measureData);
    //    matrix[0] = g_measureData.full_depth_data.distance;

    for (int i = 0; i < 9600; i++)
    {
        matrix[i] = g_measureData.full_depth_data.distance[i];
        //        std::cout << "The distance " << i+1 << ": " << matrix[i] << std::endl;
        //        std::cout << "The pointCloud " << i+1 << ": (" << data.full_depth_data.point_cloud_data.point_data[i].x << ", "
        //                  << data.full_depth_data.point_cloud_data.point_data[i].y << ", "
        //                  << data.full_depth_data.point_cloud_data.point_data[i].z << ")" << std::endl;
        return_matrix[i] = g_measureData.full_depth_data.distance[i];
    }

    //    std::cout << matrix[0] << std::endl;
    //    std::cout << sizeof(g_measureData)<< std::endl;

    HPS3D_MeasureDataFree(&g_measureData);
    // return_matrix = matrix;
    return HPS3D_RET_OK;
}

int main()
{
    int count = 0;
    int times = 1000;
    char ip_addr[] = "192.168.123.10";
    std::cout << ip_addr << std::endl;
    HPS3D_StatusTypeDef ret = connectDevice(ip_addr, 12345);
    float *return_matrix = new float[9600];
    if (ret != HPS3D_RET_OK)
    {
        printf("connect failed,Err:%d\n", ret);
        return 0;
    }
    while (count++ < times)
    {
        capture(return_matrix);
    }

    //    for (int j=0; j< 9600; ++j)
    //    {
    //        std::cout << a[j]<<std::endl;
    //    }
    disConnectDevice();
}

extern "C"
{
    void myConnectDevice(char *ip_addr, int port)
    {
        connectDevice(ip_addr, port);
    }
    int myCapture(float* return_matrix)
    {
        int rt = capture(return_matrix);
        if( rt != HPS3D_RET_OK)
        {
            // disConnectDevice();
            
            std::cout << "error"<< std::endl;
            return HPS3D_RET_ERROR;
        }
        return rt;

    }
    void myDisConnectDevice()
    {
        disConnectDevice();
    }
}
