---
title: 参与文档协作
description: 介绍如何参加文档协作
layout: doc
---
<script setup>
    import info from '@theme/components/info.vue'
    import note from '@theme/components/note.vue'
</script>
# 文档协作
<note title="注意">
commit message等内容不再重复，请查看<a href='./github.md'>协作文档</a>
</note>

## 修改内容的原因
如果实际功能与文档描述不符，请修改文档描述，而不是修改代码。

::: warning 注意
不能修改代码，只能修改内容，并需要确保修改内容与实际一致。
:::

也可以是你想修改错字，添加新的描述

或者是文档未及时更新，但是这样你建议优先提出一个issue。

## 修改方法
如果你只想修改一个文档，你可以直接点击文档页面下面的`编辑此页`来修改

但是如果你想修改很多文档，你需要下载仓库再修改。

::: warning 注意
如果要修改内容，需要提交PR而不是直接合并。
:::

### 本地配置
#### 安装环境
首先你要安装git，中国用户打开[此链接]`https://cn-git.com/`，外国用户请自行查找。
你还要同时安装nodejs,打开[此链接](https://nodejs.org/)

#### 配置 npm
npm 是 Node.js 的包管理工具，我们需要配置 npm 才能使用它。
##### 创建文件夹
打开你的 Node.js 安装目录（例如 D:\software\nodejs，之后均以此为例），手动新建两个文件夹：
```
node_global
node_cache
```

##### 执行配置命令
在终端，依次执行以下两条命令（注意替换成你自己的实际路径）：
```bash
npm config set prefix "D:\software\nodejs\node_global"
npm config set cache "D:\software\nodejs\node_cache"
```
##### 配置环境变量
如果不配置这个，以后你用 npm install -g 安装的工具都会提示“找不到命令”。

1. 在桌面右键“此电脑” -> “属性” -> “高级系统设置” -> “环境变量”。
2. 修改【系统变量】中的 `Path`：
2. 1. 找到 `Path` 变量，点击“编辑”。
2. 2. 检查是否有默认的 C 盘 npm 路径，如果有，删除它。
2. 3. 新建一条，填入你的 Node.js 安装路径：`D:\software\nodejs\`。
3. 新建/修改【用户变量】中的 Path：
3. 1. 在【用户变量】里找到 Path，点击“编辑”。
3. 2. 将默认的`C:\Users\用户名\AppData\Roaming\npm`修改为：`D:\software\nodejs\node_global`。
::: info 提示
如果没有这个`C:\Users\用户名\AppData\Roaming\npm`，就新建一条，填入你的 Node.js 安装路径。
:::
4. 新建 `NODE_PATH` 变量：
4. 1. 在【系统变量】区域，点击“新建”。
4. 2. 变量名：`NODE_PATH`
4. 3. 变量值：`D:\software\nodejs\node_global\node_modules`
4. 4. 点击确定保存所有窗口。
##### 配置镜像（对于中国开发者）
默认的 npm 源在国外，下载速度很慢。我们配置淘宝最新的镜像源，在终端输入：
```bash
npm config set registry https://registry.npmmirror.com
```
验证是否配置成功：
```bash
npm config get registry
```

若返回 `https://registry.npmmirror.com/`，说明提速成功。

#### 克隆仓库
你需要在github创建一个fork，然后克隆到本地：

你可以使用`git clone https://github.com/username/pyclickmouse.git`下载源码到本地

在**管理员终端**运行`npm install`进行安装依赖。

#### 发布和提交
你需要创建个新的分支：
```bash
git checkout -b my-branch
```
并创建一个remote链接：
```bash
git remote add origin https://github.com/username/pyclickmouse.git
```

配置你的邮箱和用户名：
```bash
git config --global user.email "your email"
git config --global user.name "your name"
```

然后，你就可以提交了。

---

在发布的时候，可能需要你的用户名和密码，所以你需要在github上设置一个key。

1. 设置好名字和到期时间，在`Repository access`选择All repositories，
2. 点击`Add permissons`，选择`Contents`，`Contents`的选择框选择`Read and write`，再选择`workflows`，确定。

然后，你就可以发布了。

#### 提交PR
你需要在[此链接](https://github.com/xystudiocode/pyclickmouse)上创建一个Pull request，然后等待review。

[点击了解PR的规范](./github.md)

打开[此链接](https://github.com/settings/personal-access-tokens/new)

#### 编译和调试
可以运行`npm run dev`打开编译环境，根据提示打开网页即可。

运行`npm run build`编译脚本，可以放到`/pyclickmouse/`目录来部署。

<note title='批注'>
但是我们会对每个提交到main分支的更改自动部署，所以你不需要自己编译。
</note>