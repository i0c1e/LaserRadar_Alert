#! /bin/bash
proc_name="alert.py"
file_name="/home/charles/code/LaserRadar_Alert/cron.log"
pid=0
proc_num()
{
    num=`ps -ef|grep $proc_name|grep -v grep|wc -l`
    return $num
}
proc_id()            # 进程号
{
 pid=`ps -ef | grep $proc_name | grep -v grep | awk '{print $2}'`
}

proc_num
number=$?

if [ $number -eq 0 ]
then 
    /opt/software/anaconda3/envs/dl/bin/python  /home/charles/code/LaserRadar_Alert/alert.py >> /home/charles/code/LaserRadar_Alert/radar.log 
    proc_id
    echo ${pid}, `date` >> $file_name
fi
