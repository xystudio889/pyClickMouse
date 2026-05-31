// 头文件
#include <windows.h>
#include <chrono>
#include <thread>

// 宏定义
#define RIGHT 0x0008 // 右键对应的id
#define LEFT 0x0002 // 左键对应的id
#define INFINITE -1 // 无限循环
#define CLICKMOUSE_VERSION 0x0006 // 版本号id

void ClickMouse(unsigned int MouseButton, unsigned int delay, unsigned int pressTime, int times = 1) {
    if (MouseButton!= RIGHT && MouseButton!= LEFT) {
        return;
    }
    // 创建一个INPUT结构体用于发送鼠标事件
    // 鼠标参数
    INPUT input;
    input.type = INPUT_MOUSE; // 鼠标事件类型
    input.mi.dx = 0; // 鼠标移动距离x轴
    input.mi.dy = 0; // 鼠标移动距离y轴
    input.mi.mouseData = 0; // 鼠标滚轮数据

    if (times != -1) {
        // 不是无限的时候的逻辑
        for (int i = 0; i < times; i++) {
            _click(input, MouseButton, delay, pressTime);
        }
    }
    else {
        // 无限循环的逻辑
        while (true) {
            _click(input, MouseButton, delay, pressTime);
        }
    }

    return;
}

// 鼠标点击的逻辑
void _click(INPUT input, unsigned int MouseButton, unsigned int delay, unsigned int pressTime){
    input.mi.dwFlags = MouseButton; // 鼠标按下
    input.mi.time = 0; // 鼠标事件时间戳
    input.mi.dwExtraInfo = 0; // 额外信息
    SendInput(1, &input, sizeof(INPUT)); // 发送鼠标事件
    std::this_thread::sleep_for(std::chrono::milliseconds(pressTime / 1000)); // 按住时间

    // 模拟鼠标释放
    input.mi.dwFlags += 2; // 鼠标释放
    SendInput(1, &input, sizeof(INPUT)); // 发送鼠标事件

    std::this_thread::sleep_for(std::chrono::milliseconds(delay / 1000)); // 延迟时间
}

// 鼠标左键的逻辑
void LeftClick(int times = 1, unsigned int delay, unsigned int pressTime) {
    ClickMouse(LEFT, delay, times, pressTime);
}

// 鼠标右键的逻辑
void RightClick(int times = 1, unsigned int delay, unsigned int pressTime) {
    ClickMouse(RIGHT, delay, times, pressTime);
}