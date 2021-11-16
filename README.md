手动编译动态链接库
```Shell
# X86
g++ -c HPS3DUser_IF.c
g++ -shared -fPIC main.cpp HPS3DUser_IF.o -lHPS3DSDK -L./ -Wl,-rpath=./  -o libConchCV.so

# arm
g++ -c HPS3DUser_IF.c
g++ -shared -fPIC main.cpp HPS3DUser_IF.o -lHPS3DSDK_arm64_1-8-0 -L./ -Wl,-rpath=./  -o libConchCV.so
```
