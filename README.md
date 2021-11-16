手动编译动态链接库
```
g++ -shared -fPIC main.cpp HPS3DUser_IF.o -lHPS3DSDK_arm64_1-8-0 -L./ -Wl,-rpath=./  -o libConchCV.so
```
