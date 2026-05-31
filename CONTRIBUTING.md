# ❓怎么贡献？
## ⬆️commit message

需要遵循以下格式:
```
更新类型(更新模块):(可选)(版本号) (更新概括):

- [(可选)子更新类型]更新内容1
- [(可选)子更新类型]更新内容2
- ...
```

更新类型有这些内容:
| 类型 | 说明 |
| --- | --- |
| ✅feat | 新功能 |
| 🔧modify | 修改功能 |
| 🐛fix | 修bug  |
| ⚒️refactor | 重构 |
| 📃docs | 改文档，比如README |
| ❇️style | 改代码风格，不影响功能 |
| 🔎test | 加测试、改测试 |
| 📆chore | 杂项，比如改.gitignore |
| ⏫perf | 性能优化  |
| 🛒ci | CI/CD相关改动 |
| 🚅build | 改构建系统或依赖 |
| ◀️revert  | 回滚 |
| 🔡dependency | 依赖更新 |
| ❌remove | 删除弃用的组件 |
| ↪️move | 移动了组件 |
| ❓unknown | 未知类型 |
| 自定义  | 尽量以一个直观的英文单词描述，最好配上emoji |

内容较多时需要对更新内容添加更新类型提示

## 🗂️分支

请按此图所示的分支结构来更新：
<img src='./imgs/readme/mergeSteps.png' alt="合并步骤" />

创建的分支需要以`feature/`开头，以表示功能分支，或创建一个fork，并在fork的分支开发。

发布pr时不限定合并分支，只要不是`main`分支都可以。

## 🔠版本号
clickmouse版本格式为：`A.B.C.D[(alpha | beta |.dev | rc) E]`
## 😊正式版本
正式版不带.dev、alpha、beta或rc后缀。

A位代表有重大更新，有代码级的变动。如1.0升级到2.0就重构了代码。

B位代表有普通更新，通常是更新一些大功能。

C位代表有修复更新，通常会更新一些小功能和一些bug。

D位代表版本代号，通常每A, B, C位有变动时候+1。也有可能A, B, C位没有变动，D位+1，这代表紧急更新，通常是修复几个重大影响的bug。

## 🅱️测试版本
测试版本带.dev、alpha、beta或rc后缀。

通常前面的`A.B.C.D`在一个测试周期内不变，代表下一个版本。

`.dev`代表早期开发更新，功能不稳定，bug很多，位于版本项目初期。这阶段新增的功能将会被放到实验室中，并默认关闭。

`alpha`代表晚期开发更新，功能不完善，bug较多，位于版本项目早期。这阶段新增的功能将会被放到实验室中，并默认关闭。

`beta`代表发布测试更新，功能完善，bug较少，不会再新增功能，位于版本项目中期，并且会逐步合并实验室中的feature。

`rc`代表预备发布版本，功能完善，bug较少，会修复一些重要安全问题或bug，最接近正式版，即将发布正式版，位于版本项目末期。

## ❓issue
- 标题格式：`[类型] 标题`
- 内容应准确写出你的需求，并选择性给出解决方案，上传截图，添加附加信息（如clickmouse版本号）
- 类型为`bug`、`enhancement`、`question`等。
- 我们给了一些模板，可直接使用。
- 使用`labels`来标记issue的类型，比如`bug`、`enhancement`、`question`等。
- 设置issue的`milestone`为你想应用的issue版本。
- 安全问题请见[安全说明文档](./SECURITY.md)。

## ❇️pr
- 标题格式：`[类型] 标题`
- 使用`labels`来标记pr的类型，比如`bug`、`enhancement`、`question`等。
- 关联issue，这样我们就可以知道这个pr解决了哪个issue。
- 需要准确写出更新内容，关联到版本号的milestone。
- 可选添加实现思路

### 🎫规范
我们pr合并的顺序为：
```mermaid
graph LR
A(其他用户的功能开发分支) --> B(develop/rp分支)
B --> C(main分支)
```

pr无特定格式，但是必须清晰描述更新内容，关联到版本号的milestone；标题要简略描述更新内容，若修复或添加了issue里的建议，把该issue编号写进该行为，若出现多个重复issue，则只用写一个，并简单描述此bug。

### ✈️快车pr
> [!WARNING]
> 快车pr请谨慎使用
- 快车pr的意思是跳过部分正常的pr合并分支步骤，以更快的合并到目标分支的功能。
- 标题格式：`[✈️快车] 标题`
- 使用快车必须在pr描述中说明使用的原因

如果有人快车合并，但没写快车合并的原因，则拒绝合并该人的分支。

快车pr有高优先级，会优先进行处理。

## 📊milestone
- 我们给每个版本都设置了一个milestone，用来管理该版本的issue和pr。
- 需要每个issue或pr都关联到一个milestone，这样我们才能知道该issue或pr是否在下个版本中添加。
- milestone格式为:`dev_版本号`

## ⬇️配置仓库
1. 下载仓库：`git clone https://github.com/xystudiocode/pyClickMouse.git`
2. 对于python版本安装python，推荐使用3.13，和软件开发者的版本一一致，[下载连接](https://www.python.org/downloads/release/python-31312/)
3. 对于头文件和dll版本，可以安装[visual studio](https://visualstudio.microsoft.com/)。
### 🖥️GUI
1. 下载源码
2. 放置一个`7z.exe`和`7z.dll`到`gui`目录
3. 安装chocolately
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```
4. 安装make工具
```powershell
choco install make
```
5. 配置python包
```powershell
pip install -r requirements.txt
```
6. 编译
```powershell
make clickmouse # 编译clickmouse
make extension # 编译扩展
make clickclean # 如果你要编译精简版，请用这个。
```
7. 运行`dist/clickmouse/clickmouse/main.exe`就可以加载clickmouse了。
### 🥴头文件
仅需修改头文件，就可以被调用
### ⚙️dll调用
使用visual studio修改`./dll/dll.sln`里的`源文件/dllmain.cpp`
### 💾gui旧版本
> [!NOTE]
> gui旧版本的再编译不接受pull request
使用visual studio修改`./ClickMouse-old/ClickMouse.sln`里的`源文件/clickmouse.cpp`
### 🐍python库调用
修改`clickmouse/`下的代码，运行`pip install .`安装
### 🦎pyd调用
修改`cython/main.py`的代码，然后执行
```python cython/setup.py build_ext --inplace```
编译结束后，该目录下应该会有个以`.pyd`结尾的文件。