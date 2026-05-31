---
title: Participating in Documentation Collaboration
description: Introduction to how to participate in documentation collaboration
layout: doc
---
<script setup>
    import info from '@theme/components/info.vue'
    import note from '@theme/components/note.vue'
</script>
# Documentation Collaboration
<note title="Note">
commit message etc. content not repeated, please check <a href='./github.md'>Collaboration Documentation</a>
</note>

## Reasons for Modifying Content
If actual functionality does not match documentation description, please modify documentation description, not modify code.

::: warning Note
Cannot modify code, only can modify content, and need to ensure modified content matches actual.
:::

Also can be you want to modify typos, add new description

Or documentation not updated in time, but this way you suggest first submit an issue.

## Modification Methods
If you only want to modify one document, you can directly click `Edit this page` below document page to modify

But if you want to modify many documents, you need to download repository then modify.

::: warning Note
If want to modify content, need to submit PR not directly merge.
:::

### Local Configuration
#### Install Environment
First you need to install git, Chinese users open [this link]`https://cn-git.com/`, foreign users please search yourself.
You also need to install nodejs, open [this link](https://nodejs.org/)

#### Configure npm
npm is Node.js package management tool, we need to configure npm to use it.
##### Create Folders
Open your Node.js installation directory (e.g. D:\software\nodejs, following examples use this), manually create two folders:
```
node_global
node_cache
```

##### Execute Configuration Commands
In terminal, execute following two commands in order (note replace with your actual path):
```bash
npm config set prefix "D:\software\nodejs\node_global"
npm config set cache "D:\software\nodejs\node_cache"
```
##### Configure Environment Variables
If not configure this, later you use npm install -g installed tools will prompt "command not found".

1. On desktop right click "This PC" -> "Properties" -> "Advanced system settings" -> "Environment Variables".
2. Modify `Path` in 【System Variables】:
2. 1. Find `Path` variable, click "Edit".
2. 2. Check if have default C drive npm path, if yes, delete it.
2. 3. Create new one, fill your Node.js installation path: `D:\software\nodejs\`.
3. Create/Modify Path in 【User Variables】:
3. 1. In 【User Variables】 find Path, click "Edit".
3. 2. Change default `C:\Users\username\AppData\Roaming\npm` to: `D:\software\nodejs\node_global`.
::: info Tip
If don't have this `C:\Users\username\AppData\Roaming\npm`, create new one, fill your Node.js installation path.
:::
4. Create `NODE_PATH` variable:
4. 1. In 【System Variables】 area, click "New".
4. 2. Variable name: `NODE_PATH`
4. 3. Variable value: `D:\software\nodejs\node_global\node_modules`
4. 4. Click OK save all windows.
##### Configure Mirror (For Chinese Developers)
Default npm source is abroad, download speed slow. We configure Taobao latest mirror source, in terminal input:
```bash
npm config set registry https://registry.npmmirror.com
```
Verify if configuration successful:
```bash
npm config get registry
```

If returns `https://registry.npmmirror.com/`, indicates speed up successful.

#### Clone Repository
You need create fork on github, then clone to local:

You can use `git clone https://github.com/username/pyClickMouse.git` download source code to local

Run `npm install` in **administrator terminal** to install dependencies.

#### Publish and Submit
You need create new branch:
```bash
git checkout -b my-branch
```
And create remote link:
```bash
git remote add origin https://github.com/username/pyClickMouse.git
```

Configure your email and username:
```bash
git config --global user.email "your email"
git config --global user.name "your name"
```

Then, you can submit.

Documentation path is at `documents/`.

---

When publishing, may need your username and password, so you need set a key on github.

1. Set name and expiration time, in `Repository access` select All repositories,
2. Click `Add permissons`, select `Contents`, `Contents` checkbox select `Read and write`, then select `workflows`, confirm.

Then, you can publish.

#### Submit PR
You need create Pull request on [this link](https://github.com/xystudiocode/pyClickMouse), then wait for review.

[Click to understand PR specifications](./github.md)

Open [this link](https://github.com/settings/personal-access-tokens/new)

#### Compile and Debug
Can run `npm run dev` open compilation environment, open webpage according to prompt.

Run `npm run build` compile script, can put in `/pyClickMouse/` directory to deploy.

<note title='Note'>
But we will automatically deploy each commit to main branch, so you don't need compile yourself.
</note>