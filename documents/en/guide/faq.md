---
layout: doc
title: Frequently Asked Questions
---

<style>
    .input_disable {
        content: url('/imgs/faq/en/light/input_disable.png')
    }

    .dark .input_disable {
        content: url('/imgs/faq/en/dark/input_disable.png')
    }

    .ipk_not_found {
        content: url('/imgs/faq/en/light/ipk_not_found.png')
    }

    .dark .ipk_not_found {
        content: url('/imgs/faq/en/dark/ipk_not_found.png')
    }

    .stop_click {
        content: url('/imgs/faq/en/light/stop_click.png')
    }

    .dark .stop_click {
        content: url('/imgs/faq/en/dark/stop_click.png')
    }

    .update_disable {
        content: url('/imgs/faq/en/light/update_disable.png')
    }

    .dark .update_disable {
        content: url('/imgs/faq/en/dark/update_disable.png')
    }

    .lang_not_found {
        content: url('/imgs/faq/light/lang_not_found.png')
    }

    .dark .lang_not_found {
        content: url('/imgs/faq/dark/lang_not_found.png')
    }
</style>

<script setup>
    import important from '@theme/components/important.vue'
</script>

# Frequently Asked Questions

<important title='Important'>
All paths in this page are relative to the clickmouse installation directory.
If Windows cannot open the files mentioned inside, please try opening with Notepad.
</important>

## Errors

**1. Language pack does not exist:**

Please check if there is a langs directory in clickmouse's `res` directory. If yes, check if there is a `langs.json` file inside. If not, please reinstall clickmouse. [Download link](https://github.com/xystudiocode/pyclickmouse/releases/latest)

<img class='lang_not_found' alt='Language pack not found' />

**2. Cannot start:**

There might be some bugs. You can modify the content in `packages.json` to:
```json
["xystudio.clickmouse", "xystudio.clickmouse.repair"]
```
Then run the `repair.exe` file in the current directory, check the content you want to clear, click the `Repair` button, and start clickmouse again to see.

::: tip Tip
It is recommended to select all repair items, but this will delete all user data and extensions, restoring to initial state.
:::

If you can compile source code, you can also try using makefile, remove the `--windows-console-mode=disable` from compiling source code to get error stack trace.

If still not working, try uninstalling and reinstalling clickmouse. [Download link](https://github.com/xystudiocode/pyclickmouse/releases/latest)

If the problem persists, you can [report an issue](https://github.com/xystudiocode/pyClickMouse/issues/new/choose)

**3. Cannot connect to update, showing `timeout`:**

Our update content is stored on GitHub, and the network in China is slower.

You can install [watt toolkit](https://gitee.com/rmbgame/SteamTools/releases/download/3.0.0-rc.16/Steam%20%20_v3.0.0-rc.16_win_x64.exe)
Then:
1. Open watt toolkit, click `Network Acceleration` on the left
2. Check `github`
3. Click `One-click Acceleration`

> This method can only ensure no timeout error, but cannot guarantee fast network speed.

If still not working, I have no more methods

## Software Function Usage Issues
**1. Why is the click button grayed out?**

You may not have correctly entered click delay and click count. You can set click time and click count in the input boxes below, and select the unit for click count/delay in the dropdown box.

::: warning Note
Need to enter correct numbers, otherwise clicking will fail.
:::

**2. Click input box is grayed out/cannot open click settings**

This may be because you are currently clicking, need to click the `Stop` button to stop before entering again.

<img class='input_disable' alt='Click input box grayed out' />
<br />
<img class='stop_click' alt='Cannot open click settings' />

**3. Software update failed: Update service not enabled**

Please go to `Settings`, select `Update` on the left, then enable `Enable Update`

<img class='update_disable' alt='Update service not enabled' />

**4. Prompt that package manager folder does not exist, pops up every time**

You can go to Settings - Notifications - turn off `Official extension package missing warning`

<img class='ipk_not_found' alt='Prompt that package manager folder does not exist' />

**5. Checkbox click invalid**

You may have clicked on the text area. Clickmouse checkbox needs to be clicked inside the box to be effective.