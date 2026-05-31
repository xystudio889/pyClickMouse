// ClickMouse.cpp : 定义应用程序的入口点。
//

#include "framework.h"
#include "ClickMouse.h"
#include "shellapi.h"
#include "windows.h"

#define MAX_LOADSTRING 100

// 全局变量:
HINSTANCE hInst;                                // 当前实例
WCHAR szTitle[MAX_LOADSTRING];                  // 标题栏文本
WCHAR szWindowClass[MAX_LOADSTRING];            // 主窗口类名
UINT_PTR g_TimerId = 0;                // 定时器ID
bool g_IsPaused = false;               // 暂停状态
int g_CurrentClick = 0;                // 当前点击类型 0:无 1:左键 2:右键
int g_Interval = 0;                    // 点击间隔
WCHAR g_szInterval[100] = {  0 };         // 保存合法的间隔值文本
HWND g_hTargetWnd = NULL;
bool g_UseForceFocus = true; // 是否启用强制焦点

// 此代码模块中包含的函数的前向声明:
ATOM                MyRegisterClass(HINSTANCE hInstance);
BOOL                InitInstance(HINSTANCE, int);
LRESULT CALLBACK    WndProc(HWND, UINT, WPARAM, LPARAM);
INT_PTR CALLBACK    About(HWND, UINT, WPARAM, LPARAM);
INT_PTR CALLBACK    UpdateLog(HWND, UINT, WPARAM, LPARAM);

bool IsRunAsAdmin() {
    SID_IDENTIFIER_AUTHORITY NtAuthority = SECURITY_NT_AUTHORITY;
    PSID AdministratorsGroup;
    BOOL isAdmin = FALSE;

    if (AllocateAndInitializeSid(&NtAuthority, 2, SECURITY_BUILTIN_DOMAIN_RID,
        DOMAIN_ALIAS_RID_ADMINS, 0, 0, 0, 0, 0, 0, &AdministratorsGroup)) {
        CheckTokenMembership(NULL, AdministratorsGroup, &isAdmin);
        FreeSid(AdministratorsGroup);
    }
    return isAdmin;
}

// 窗口焦点处理函数
bool EnsureTargetFocus(HWND hDlg) {
    // 获取当前前景窗口
    HWND hForeground = GetForegroundWindow();

    // 如果已经是目标窗口且未启用强制聚焦
    if (hForeground == g_hTargetWnd && !g_UseForceFocus)
        return true;

    // 使用更精确的窗口匹配算法
    DWORD dwForegroundPID;
    GetWindowThreadProcessId(hForeground, &dwForegroundPID);

    // 检查窗口有效性
    if (!IsWindowVisible(hForeground) || IsIconic(hForeground)) {
        MessageBox(hDlg, L"目标窗口不可用\n错误描述：目标窗口不可见或最小化。", L"错误", MB_ICONERROR);
        return false;
    }

    // 使用AttachThreadInput实现精确输入控制
    DWORD dwCurrentThread = GetCurrentThreadId();
    DWORD dwTargetThread = GetWindowThreadProcessId(hForeground, NULL);

    if (dwCurrentThread != dwTargetThread) {
        AttachThreadInput(dwCurrentThread, dwTargetThread, TRUE);
    }

    // 使用渐进式聚焦策略
    SetWindowPos(hForeground, HWND_TOPMOST, 0, 0, 0, 0,
        SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE);
    SetWindowPos(hForeground, HWND_NOTOPMOST, 0, 0, 0, 0,
        SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE);

    // 发送扩展聚焦消息（绕过某些应用程序的限制）
    SendMessageTimeout(hForeground, WM_MOUSEACTIVATE, 0, 0,
        SMTO_NORMAL, 100, NULL);

    // 使用低级别键盘事件触发聚焦
    INPUT input[4] = { 0 };
    input[0].type = INPUT_KEYBOARD;
    input[0].ki.wVk = VK_MENU;
    input[1].type = INPUT_KEYBOARD;
    input[1].ki.wVk = VK_TAB;
    input[2].type = INPUT_KEYBOARD;
    input[2].ki.wVk = VK_TAB;
    input[2].ki.dwFlags = KEYEVENTF_KEYUP;
    input[3].type = INPUT_KEYBOARD;
    input[3].ki.wVk = VK_MENU;
    input[3].ki.dwFlags = KEYEVENTF_KEYUP;
    SendInput(4, input, sizeof(INPUT));

    // 解除线程绑定
    if (dwCurrentThread != dwTargetThread) {
        AttachThreadInput(dwCurrentThread, dwTargetThread, FALSE);
    }

    return (GetForegroundWindow() == hForeground);
}

// 定时器处理函数
VOID CALLBACK EnhancedTimerProc(HWND hwnd, UINT msg, UINT_PTR id, DWORD time) {
    static bool bFocusEnsured = false;

    // 首次尝试聚焦
    if (!bFocusEnsured) {
        if (!EnsureTargetFocus(GetParent(hwnd))) {
            KillTimer(hwnd, id);
            MessageBox(GetParent(hwnd), L"无法获取窗口焦点\n错误描述：你的程序不支持此工具。", L"错误", MB_ICONERROR);
            return;
        }
        bFocusEnsured = true;
    }

    // 获取窗口实际位置（考虑DPI缩放）
    RECT rcWindow;
    if (!GetWindowRect(g_hTargetWnd, &rcWindow)) {
        KillTimer(hwnd, id);
        MessageBox(GetParent(hwnd), L"无法获取窗口尺寸\n错误描述：你的程序不支持此工具。", L"错误", MB_ICONERROR);
        return;
    }

    // 生成智能点击坐标（避开边缘区域）
    int x = rcWindow.left + (rcWindow.right - rcWindow.left) * 0.5;
    int y = rcWindow.top + (rcWindow.bottom - rcWindow.top) * 0.5;

    // 使用混合输入法发送事件
    INPUT inputs[4] = { 0 };

    // 鼠标按下
    inputs[0].type = INPUT_MOUSE;
    inputs[0].mi.dx = x * (65535 / GetSystemMetrics(SM_CXSCREEN));
    inputs[0].mi.dy = y * (65535 / GetSystemMetrics(SM_CYSCREEN));
    inputs[0].mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE;

    inputs[1].type = INPUT_MOUSE;
    inputs[1].mi.dwFlags = (g_CurrentClick == 1) ? MOUSEEVENTF_LEFTDOWN : MOUSEEVENTF_RIGHTDOWN;

    // 鼠标释放
    inputs[2].type = INPUT_MOUSE;
    inputs[2].mi.dwFlags = (g_CurrentClick == 1) ? MOUSEEVENTF_LEFTUP : MOUSEEVENTF_RIGHTUP;

    // 添加随机移动防止检测
    inputs[3].type = INPUT_MOUSE;
    inputs[3].mi.dx = (x + rand() % 5 - 2) * (65535 / GetSystemMetrics(SM_CXSCREEN));
    inputs[3].mi.dy = (y + rand() % 5 - 2) * (65535 / GetSystemMetrics(SM_CYSCREEN));
    inputs[3].mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE;

    SendInput(4, inputs, sizeof(INPUT));
}

void LeftClick() {
    // 创建一个INPUT结构体用于发送鼠标事件
    INPUT input;
    input.type = INPUT_MOUSE;
    input.mi.dx = 0;
    input.mi.dy = 0;
    input.mi.mouseData = 0;
    input.mi.dwFlags = MOUSEEVENTF_LEFTDOWN; // 鼠标左键按下
    input.mi.time = 0;
    input.mi.dwExtraInfo = 0;
    SendInput(1, &input, sizeof(INPUT));

    // 模拟鼠标左键释放
    input.mi.dwFlags = MOUSEEVENTF_LEFTUP; // 鼠标左键释放
    SendInput(1, &input, sizeof(INPUT));
}

void RightClick() {
    // 创建一个INPUT结构体用于发送鼠标事件
    INPUT input;
    input.type = INPUT_MOUSE;
    input.mi.dx = 0;
    input.mi.dy = 0;
    input.mi.mouseData = 0;
    input.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN; // 鼠标右键按下
    input.mi.time = 0;
    input.mi.dwExtraInfo = 0;
    SendInput(1, &input, sizeof(INPUT));

    // 模拟鼠标右键释放
    input.mi.dwFlags = MOUSEEVENTF_RIGHTUP; // 鼠标右键释放
    SendInput(1, &input, sizeof(INPUT));
}

// 对话框消息处理函数
INT_PTR CALLBACK MainDlgProc(HWND hDlg, UINT message, WPARAM wParam, LPARAM lParam)
{
    switch (message)
    {
    case WM_COMMAND:
    {
        int wmId = LOWORD(wParam);
        switch (wmId)
        {
        case IDM_ABOUT:
            DialogBox(GetModuleHandle(NULL),
                MAKEINTRESOURCE(IDD_ABOUTBOX),
                hDlg, About);
            break;
        case IDM_UPDATE:
            ShellExecuteW(NULL, L"open", L"https://github.com/xystudio889/ClickMouse/releases/latest", NULL, NULL, SW_SHOWNORMAL);
            break;
        case IDM_UPDATE_LOG:
            DialogBox(GetModuleHandle(NULL),
                MAKEINTRESOURCE(IDD_UPDATE_LOG),
                hDlg, UpdateLog);
            break;
        case IDM_EXIT:
            SendMessage(hDlg, WM_CLOSE, 0, 0);
            break;
        case IDC_LEFT:   // 左键连点按钮
        case IDC_RIGHT:  // 右键连点按钮
        {
            // 停止现有定时器
            if (g_TimerId) {
                KillTimer(hDlg, g_TimerId);
                g_TimerId = 0;
            }

            // 获取并验证间隔时间
            WCHAR szInterval[100];
            GetDlgItemText(hDlg, IDC_DELAY_INPUT_BOX, szInterval, 100);

            // 检查是否为纯数字
            bool valid = true;
            for (int i = 0; szInterval[i]; i++) {
                if (!iswdigit(szInterval[i])) {
                    valid = false;
                    break;
                }
            }

            if (!valid || wcslen(szInterval) == 0) {
                MessageBox(hDlg, L"请输入有效的数字间隔", L"错误", MB_ICONERROR);
                return TRUE;
            }

            // 保存合法值
            wcscpy_s(g_szInterval, szInterval);
            g_Interval = _wtoi(szInterval);

            // 设置新的点击类型
            g_CurrentClick = (wmId == IDC_LEFT) ? 1 : 2;

            // 启动定时器
            g_TimerId = SetTimer(hDlg, 1, g_Interval, EnhancedTimerProc);  // 使用回调函数
            SetDlgItemText(hDlg, IDC_PAUSE, L"暂停");
            break;
        }

        case IDC_PAUSE:  // 暂停/重启按钮
        {
            if (g_CurrentClick != 0) {
                if (g_IsPaused) {
                    // 重启定时器
                    g_TimerId = SetTimer(hDlg, 1, g_Interval, NULL);
                    if (g_TimerId) {
                        SetDlgItemText(hDlg, IDC_PAUSE, L"暂停");
                        g_IsPaused = false;
                    }
                }
                else {
                    // 暂停定时器
                    if (KillTimer(hDlg, 1)) {
                        g_IsPaused = true;
                        SetDlgItemText(hDlg, IDC_PAUSE, L"重启");
                    }
                }
            }
            break;
        }

        case IDC_STOP:  // 停止按钮
        {
            if (g_CurrentClick) {
                KillTimer(hDlg, 1);
                g_TimerId = 0;
                g_CurrentClick = 0;
                g_IsPaused = false;
                SetDlgItemText(hDlg, IDC_PAUSE, L"暂停");
            }
            break;
        }
        }
        break;
    }

    case WM_TIMER:
    {
        if (wParam == 1) {
            if (g_CurrentClick == 1) {
                LeftClick();
            }
            else if (g_CurrentClick == 2) {
                RightClick();
            }
        }
        break;
    }

    case WM_PAINT:
    {
        PAINTSTRUCT ps;
        BeginPaint(hDlg, &ps);
        EndPaint(hDlg, &ps);
        return TRUE;
    }

    case WM_CLOSE:
        if (g_TimerId) {
            KillTimer(hDlg, g_TimerId);
        }
        EndDialog(hDlg, 0);
        return TRUE;

    default:
        return FALSE;
    }
    return TRUE;
}


// 入口点
int APIENTRY wWinMain(_In_ HINSTANCE hInstance,
    _In_opt_ HINSTANCE hPrevInstance,
    _In_ LPWSTR    lpCmdLine,
    _In_ int       nCmdShow)
{
    // 创建基于资源的主对话框
    DialogBoxParamW(
        hInstance,
        MAKEINTRESOURCEW(IDD_MAIN_WINDOW),
        NULL,
        MainDlgProc,  // 新的对话框过程函数
        (LPARAM)0
    );
    return 0;
}


//
//  函数: MyRegisterClass()
//
//  目标: 注册窗口类。
//
ATOM MyRegisterClass(HINSTANCE hInstance)
{
    WNDCLASSEXW wcex = { 0 };

    wcex.cbSize = sizeof(WNDCLASSEX);

    wcex.style          = CS_HREDRAW | CS_VREDRAW;
    wcex.lpfnWndProc    = MainDlgProc;
    wcex.cbClsExtra     = 0;
    wcex.cbWndExtra     = 0;
    wcex.hInstance      = hInstance;
    wcex.hCursor        = LoadCursor(nullptr, IDC_ARROW);
    wcex.hbrBackground  = (HBRUSH)(COLOR_WINDOW+1);
    wcex.lpszMenuName   = MAKEINTRESOURCEW(IDC_CLICKMOUSE);
    wcex.lpszClassName  = szWindowClass;
    wcex.cbSize = sizeof(WNDCLASSEX);
    wcex.hIcon = LoadIcon(hInstance, MAKEINTRESOURCE(IDI_CLICKMOUSE));
    wcex.hIconSm = LoadIcon(hInstance, MAKEINTRESOURCE(IDI_CLICKMOUSE));

    return RegisterClassExW(&wcex);
}

//
//   函数: InitInstance(HINSTANCE, int)
//
//   目标: 保存实例句柄并创建主窗口
//
//   注释:
//
//        在此函数中，我们在全局变量中保存实例句柄并
//        创建和显示主程序窗口。
//
BOOL InitInstance(HINSTANCE hInstance, int nCmdShow)
{
   hInst = hInstance; // 将实例句柄存储在全局变量中

   HWND hWnd = CreateWindowW(szWindowClass, szTitle, WS_OVERLAPPEDWINDOW,
      CW_USEDEFAULT, 0, CW_USEDEFAULT, 0, nullptr, nullptr, hInstance, nullptr);

   if (!hWnd)
   {
      return FALSE;
   }

   ShowWindow(hWnd, nCmdShow);
   UpdateWindow(hWnd);

   return TRUE;
}

// “关于”框的消息处理程序。
INT_PTR CALLBACK About(HWND hDlg, UINT message, WPARAM wParam, LPARAM lParam)
{
    UNREFERENCED_PARAMETER(lParam);
    switch (message)
    {
    case WM_INITDIALOG:
        // 启用DPI感知
        SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
        // 申请管理员权限
        if (!IsRunAsAdmin()) {
            ShellExecute(NULL, L"runas", GetCommandLine(), NULL, NULL, SW_SHOWNORMAL);
        }
        return (INT_PTR)TRUE;

    case WM_COMMAND:
        if (LOWORD(wParam) == IDOK || LOWORD(wParam) == IDCANCEL)
        {
            EndDialog(hDlg, LOWORD(wParam));
            return (INT_PTR)TRUE;
        }
        else if (LOWORD(wParam) == IDSTAR)
        {
            ShellExecuteW(NULL, L"open", L"https://github.com/xystudio889/ClickMouse/", NULL, NULL, SW_SHOWNORMAL);
        }
        break;
    }
    return (INT_PTR)FALSE;
}

// “更新日志”框的消息处理程序。
INT_PTR CALLBACK UpdateLog(HWND hDlg, UINT message, WPARAM wParam, LPARAM lParam)
{
    UNREFERENCED_PARAMETER(lParam);
    switch (message)
    {
    case WM_INITDIALOG:
        // 启用DPI感知
        SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
        // 申请管理员权限
        if (!IsRunAsAdmin()) {
            ShellExecute(NULL, L"runas", GetCommandLine(), NULL, NULL, SW_SHOWNORMAL);
        }
        return (INT_PTR)TRUE;

    case WM_COMMAND:
        if (LOWORD(wParam) == IDOK || LOWORD(wParam) == IDCANCEL)
        {
            EndDialog(hDlg, LOWORD(wParam));
            return (INT_PTR)TRUE;
        }
        else if (LOWORD(wParam) == IDSHOW_MORE_UPDATE_LOG)
        {
            ShellExecuteW(NULL, L"open", L"https://github.com/xystudio889/ClickMouse/releases", NULL, NULL, SW_SHOWNORMAL);
        }
        break;
    }
    return (INT_PTR)FALSE;
}
