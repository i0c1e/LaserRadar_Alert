手动编译动态链接库
```Shell
# X86
g++ -c HPS3DUser_IF.c
g++ -std=c++11 -shared -fPIC main.cpp HPS3DUser_IF.o -I./ -Ispdlog -lHPS3DSDK -lspdlog -L./ -Wl,-rpath=./  -o libConchCV.so

# arm
g++ -c HPS3DUser_IF.c
g++ -std=c++11 -shared -fPIC main.cpp HPS3DUser_IF.o -I./ -Ispdlog -lHPS3DSDK_arm64_1-8-0 -lspdlog -L./ -Wl,-rpath=./  -o libConchCV.so


nohup python3 alert.py  --ip 10.106.40.221 --command > /dev/null 2>&1 &
```
