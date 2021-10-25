手动编译动态链接库
```
g++ -shared -fPIC main.cpp HPS3DUser_IF.o -lHPS3DSDK -L./ -Wl,-rpath=./ -o libCV.so
```