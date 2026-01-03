>[!NOTE]
> 若你是普通人，请下载`clickmouse-python-gui-版本号-windows-amd64.7z`并解压到一个文件夹，若你是python开发人员，且要下载`clickmouse`的本地包(网络可行时候推荐使用`pip install clickmouse`)，请下载`clickmouse-2.1.1-py3-none-any.whl`或`clickmouse-2.1.1.tar.gz`，若你是C/C++开发人员，请下载`clickMouse.h`，旧版clickmouse已经放到`ClickMouse-c-windows-amd64-1.0.2.3.exe`中

>[!IMPORTANT]
> 更新时候删除所有的文件和文件夹，但是要保留data文件夹，要不然用户数据将会丢失。

## 更新信息


## 已知问题
- 暂无已知问题

## 下个版本预告
见#15

## 数据版本
`clickmouse.h`的版本为6
输入以下C++代码检查你的clickmouse版本
```cpp
#include<iostream>
#include<clickmouse.h>
using namespace std;

int main(){
    cout << CLICKMOUSE_VERSION // 若报错，则你的clickmouse版本为1.0.2.2及以前
}
```

python库调用或pyd调用文件版本号为2.1.1
> [!TIP]
> 下载基于pyd的文件时候需要注意:必须下载是你python版本的文件(如`lickmouse.cp39-win_amd64.pyd`)仅支持python3.9(cp后面的是版本，如果你使用python3.13以后的版本，不需要下载后面有t的版本(除非你使用free thread开发))`

输入以下python代码检查你的clickmouse版本
```python
import clickmouse

print(clickmouse.__version__)
```

更多测试的代码请查阅[readme](https://github.com/xystudio889/pyClickMouse/blob/main/README.md)
