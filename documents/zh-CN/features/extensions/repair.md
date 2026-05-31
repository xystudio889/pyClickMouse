---
title: 修复软件
description: 修复clickmouse的问题
layout: doc
---

<script setup>
    import note from '@theme/components/note.vue'
</script>

# 功能

如果你的clickmouse软件出现问题，你可以在不重装软件的清情况下进行尽可能的修复。

## 修复项

- 缓存：清除错误的缓存文件，并重新构建来解决问题。（不会清除更新缓存）
- 更新缓存：重置更新缓存，并重新构建来解决问题。
- 扩展文件：移除所有的扩展文件，以尝试解决扩展冲突。
- 安装信息注册表：将会重置clickmouse的注册表信息，这样你可以再次运行初始化程序。
- 软件数据：删除clickmouse的软件数据，并重新安装来解决问题。
- 首次运行文件：如果删除，将会自动重新运行初始化程序。

<note title='批注'>如果你全选修复项后修复，将会恢复到新装状态，但是要你的<code>res</code>仍然完整就可以全新安装。</note>

## 打开方式
1. 安装扩展：clickmouse 修复
1. 1. 打开clickmouse，选择扩展-官方扩展-修改扩展；
1. 2. 点击“安装”按钮，选择要修复的扩展；
1. 3. 等待安装完成，点击“完成”按钮，并重启软件；
2. 点击扩展-官方扩展-修复；
3. 根据提示关闭软件和其托盘图标，然后将会启动修复程序；

## 急救方案
如果你主程序无法使用，你可以打开**管理员**终端，运行`./install_pack --ipk`来启动包管理器。

然后你再运行`repair.exe`来进行修复

如果你的包管理器也被损毁了，你可以修改packages.json，修改为以下内容:
```json
["xystudio.clickmouse", "xystudio.clickmouse.repair"]
```
然后再运行`repair.exe`来进行修复。
