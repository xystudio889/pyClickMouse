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
| 🐛fix | 修bug  |
| ⚒️refactor |  重构，不新增功能，也不修bug |
| 📃docs | 改文档，比如README |
| ❇️style | 改代码风格，不影响功能 |
| 🔎test | 加测试、改测试 |
| 📆chore | 杂项，比如改.gitignore |
| ⏫perf | 性能优化  |
| 🛒ci | CI/CD相关改动 |
| 🚅build | 改构建系统或依赖 |
| ◀️revert  | 回滚某个提交 |
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

发布pr时要选择**合并到`develop`分支**。

## 🔠版本号
版本号格式使用语义化版本号，具体规则如下：
```
A.B.C.D((.dev | alpha | beta | rc)E)
```

- A: 主版本号，当有重大功能更新时，比如重构等。
- B: 次版本号，当有新功能或功能改进时，比如增加新功能。
- C: 修订号，当有bug修复或功能改进时，比如修复bug等。
- D: 开发版本号，每发布一个正式版，D位版本号加1。
- (.dev | alpha | beta | rc): 测试版本阶段，dev表示开发版，alpha表示内部测试版，beta表示公开测试版，rc表示候选版本，E位越大版本越新，且在开发阶段更新时E为变为1，在.dev时候以0开始。版本新旧顺序为.dev < alpha < beta < rc。

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
A(其他用户的功能开发分支) --> B(develop分支)
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
1. 下载源码
2. 放置一个`7z.exe`和`7z.dll`到`gui`目录
3. 在github上制作一个api key，把密钥填入`gui/hooks/keycrpytr.py`的data变量中(格式为`{"github": "你的api key"}`),使用`cd gui&&runhook keycrpyter&&cd..`,把运行输出的结果同时放到`gui/key`和`gui/res/default_key`中
4. 使用`make extension`编译扩展，放入`gui/res/packages`目录下
5. 使用`make clickmouse`制作clickmouse的安装包,把`dist/clickmouse/`下的所有除了`main.dist`和`updater.dist`的.dist文件夹的**子文件**移动到`dist/clickmouse/main.dist`下
> [!WARNING]
> 请不要直接把这些文件夹复制，要把子文件复制，否则程序无法运行
6. 把`dist/clickmouse/updater.dist`重命名为`updater`后**把整个文件夹**移动到`main.dist`下
> [!WARNING]
> 请不要直接把`updater`的子文件复制，要把整个文件夹复制，否则程序无法运行
7. 可选择把`dist/clickmouse/main.dist`这个文件夹重命名
8. 运行`main.exe`就可以加载clickmouse了。