// dllmain.cpp : 定义 DLL 应用程序的入口点。
#include <windows.h>
#include <chrono>
#include <thread>
#define RIGHT 0x0008
#define LEFT 0x0002
#define INFINITE -1
#define CLICKMOUSE_VERSION 0x0003

void MouseClick(unsigned int MouseButton, unsigned int delay, int times = 1) {
    if (MouseButton!= RIGHT && MouseButton!= LEFT) {
        return;
    }
    // 创建一个INPUT结构体用于发送鼠标事件
    INPUT input;
    input.type = INPUT_MOUSE;
    input.mi.dx = 0;
    input.mi.dy = 0;
    input.mi.mouseData = 0;
    if (times != -1) {
        for (int i = 0; i < times; i++) {
            input.mi.dwFlags = MouseButton; // 鼠标按下
            input.mi.time = 0;
            input.mi.dwExtraInfo = 0;
            SendInput(1, &input, sizeof(INPUT));
            std::this_thread::sleep_for(std::chrono::milliseconds(delay / 1000));

            // 模拟鼠标释放
            input.mi.dwFlags += 2; // 鼠标释放
            SendInput(1, &input, sizeof(INPUT));
        }
    }
    else {
        while (true) {
            input.mi.dwFlags = MouseButton; // 鼠标按下
            input.mi.time = 0;
            input.mi.dwExtraInfo = 0;
            SendInput(1, &input, sizeof(INPUT));
            std::this_thread::sleep_for(std::chrono::milliseconds(delay / 1000));

            // 模拟鼠标释放
            input.mi.dwFlags += 2; // 鼠标释放
            SendInput(1, &input, sizeof(INPUT));
        }
    }

    return;
}