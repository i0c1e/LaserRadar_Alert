//
// Created by charles on 10/21/21.
//

#include "a.h"
#include <iostream>

void hii()
{
    std::cout<< "cpp-hi" << std::endl;
}

extern "C"{
    void hello(){
        return hii();
    }
}