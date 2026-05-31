---
title: issue模板
description: 在线查看issue模板
layout: doc
---

<script setup>
import note from '@theme/components/note.vue'
import subtitle from '@theme/components/subtitle.vue'
import strongCard from '@theme/components/strongCard.vue'
import ginput from '@theme/components/ginput.vue'
import important from '@theme/components/important.vue'
import tip from '@theme/components/tip.vue'
import choiceBox from '@theme/components/choiceBox.vue'
import mdinput from '@theme/components/mdinput.vue'
</script>

<script>
export default {
  components: {
    choiceBox
  },
  data() {
    return {
      defaultOfficalSelect: 'official',
      officalOptions: [
        { value: 'official', label: '✅是' },
        { value: 'unofficial', label: '❌不是' },
        { value: 'dontknow', label: '❓我不知道/忘记了' }
      ],
      moduleOptions: [
        { value: 'Clicker',label: '🖱️连点功能' },
        { value: 'Calculator',label: '🧮实时计算和判断连点延迟(包括主窗口，设置和快速连点)' },
        { value: 'Setting',label: '⚙️设置' },
        { value: 'Theme',label: '✳️自适应主题色切换' },
        { value: 'Hotkey',label: '⌨️热键' },
        { value: 'Tray',label: '️⬜托盘应用' },
        { value: 'OtherMain',label: '☁️其他主程序功能' },
        { value: 'Init',label: '⬇️初始化程序' },
        { value: 'PackageManager',label: '📦包管理器(包括初始化的包管理器)' },
        { value: 'Uninstall',label: '🗑️卸载程序' },
        { value: 'Update',label: '🔄️检查更新服务' },
        { value: 'Fix',label: '🔧修复程序' },
        { value: 'Install',label: '⤴️安装更新' },
        { value: 'Extension',label: '💠其他扩展' },
        { value: 'Clean',label: '♻️清理缓存' },
        { value: 'Theme/Style',label: '🏳️‍🌈主题/样式' },
        { value: 'Document',label: '📄文档' },
        { value: 'clickClean',label: '🟦clickClean'},
        { value: 'Unknown',label: '❓其他/未知' },
      ],
      idea_text: '- 解决方案1：\n- 1. 解决步骤1\n- 2. 解决步骤2\n- 3. 解决步骤3\n- 4. 解决步骤...\n- 解决方案2：\n- 1. 解决步骤1\n- 2. 解决步骤2\n- 3. 解决步骤3\n- 4. 解决步骤...\n- 解决方案3：\n- 1. 解决步骤1\n- 2. 解决步骤2\n- 3. 解决步骤3\n- 4. 解决步骤...\n- 解决方案...',
      langPack: {
        Write: '撰写',
        Preview: '预览',
        More: '更多',
        H3: '标题',
        Bold: '加粗',
        Italic: '斜体',
        Quote: '引用',
        Code: '代码',
        Link: '链接',
        UnOrderedList: '无序列表',
        NumList: '数字列表',
        TaskList: '任务列表',
        AddFile: '复制，拖动或选择文件到此处。',
        Nothing: '没有要预览的内容。'
      },
      feature_reason: '解决了什么问题?\n改进了什么?\n其他原因...',
      task_idea: `- 新功能1:
- - 实行方案1:
- - 1. 实行步骤1
- - 2. 实行步骤2
- - 3. 实行步骤3
- - 4. 实行步骤...
- - 实行方案2:
- - 1. 实行步骤1
- - 2. 实行步骤2
- - 3. 实行步骤3
- - 4. 实行步骤...
- - 实行方案3:
- - 1. 实行步骤1
- - 2. 实行步骤2
- - 3. 实行步骤3
- - 4. 实行步骤...
- - 其他实行方案...
- 新功能2:
- - 实行方案1:
- - 1. 实行步骤1
- - 2. 实行步骤2
- - 3. 实行步骤3
- - 4. 实行步骤...
- - 实行方案2:
- - 1. 实行步骤1
- - 2. 实行步骤2
- - 3. 实行步骤3
- - 4. 实行步骤...
- - 实行方案3:
- - 1. 实行步骤1
- - 2. 实行步骤2
- - 3. 实行步骤3
- - 4. 实行步骤...
- - 其他实行方案...
- 新功能3:
- - 实行方案1:
- - 1. 实行步骤1
- - 2. 实行步骤2
- - 3. 实行步骤3
- - 4. 实行步骤...
- - 实行方案2:
- - 1. 实行步骤1
- - 2. 实行步骤2
- - 3. 实行步骤3
- - 4. 实行步骤...
- - 实行方案3:
- - 1. 实行步骤1
- - 2. 实行步骤2
- - 3. 实行步骤3
- - 4. 实行步骤...
- - 其他实行方案...
- 其他功能...`,
    ChoicePlace: '无',
    CardLangPack: {
      Assignee: '指派者',
      LabelDesc: '标签',
      TypeDesc: '类型',
      Project: '项目',
      Milestone: '里程碑',
      Product: '记住，贡献到这个仓库的任何内容都应该遵循其',
      GuideLines: '贡献指南',
      Security: '安全政策',
      And: '和',
      CreateMore: '创建更多',
      Cancel: '取消',
      Create: '创建',
      Priority: '优先级',
      Effort: '影响',
      StartDate: '开始日期',
      TargetDate: '结束日期',
    },
    bugLabel: {
      Label: 'bug',
      Type: 'Bug'
    },
    featureLabel: {
      Label: 'enhancement',
      Type: 'Feature'
    },
    taskLabel: {
      Label: "enhancement",
      Type: "Task"
    }
    }
  }
}
</script>
<style scoped>
.desc {
    color: #9198a1;
    font-size: 12px;
    margin: 0;
    margin-bottom: 0.75rem;
}
a, a:hover { 
  color: #0969da;
}
</style>

# issue模板

## Bug报告

报告一个bug。
<br />
<strongCard LabelColor='#d73a4a' TypeColor='#f85149' :LangPack='{...CardLangPack, ...bugLabel}'>
<subtitle required='true' noTopMargin='true'>添加一个标题</subtitle>
<ginput text='🐛[BUG]'></ginput>
<note title='批注'>为避免造成更多的麻烦，请在报告issue前，先检查是否有其他人已经报告过相同的问题。<a href="https://github.com/xystudiocode/pyclickmouse/issues">检查是否存在重复</a>😊</note>
<important title='注意'>我们不会在gitee上处理issue，请使用github发布。🙋‍♂️</important>
<tip title='提示'>请一次只报告1个问题。😀</tip>
<subtitle required='true' desc='反馈三位或四位版本号，可前往"帮助" - "关于"界面查看当前clickmouse版本号'>🔡Clickmouse版本</subtitle>
<ginput text='' place='X.X.X 或 X.X.X.X'></ginput>
<subtitle required='true'>🎭你是否从官方版本发现bug</subtitle>
<p class="desc">❗clickmouse官方版本只在<a href="https://github.com/xystudiocode/pyclickmouse/releases">github releases</a>或<a href="https://gitee.com/xystudiocode/pyclickmouse/releases">gitee releases</a>页面发布，其他均为非官方版本。</p>
<choiceBox :placeholder='ChoicePlace' v-model='defaultOfficalSelect' :options='officalOptions'>
</choiceBox>
<br />
<subtitle required='true' desc='🐛请选择你运行出现bug的模块，可以多选。'>🐛你运行出现bug的模块</subtitle>
<choiceBox :placeholder='ChoicePlace' multiple='true' :options='moduleOptions'></choiceBox>
<subtitle required='true' desc='🐍bug描述'>🐍描述你的bug。</subtitle>
<mdinput placeholder='请在这描述' :LangPack='langPack'></mdinput>
<subtitle required='false' desc='🔦描述这个bug的影响。'>🔦这个bug的影响。</subtitle>
<mdinput placeholder='请在这描述' :LangPack='langPack'></mdinput>
<subtitle required='false' desc='🔧描述如何重现这个bug。'>📝重现步骤</subtitle>
<mdinput placeholder='1. 步骤1&#10;2. 步骤2&#10;3. 步骤3&#10;4. 步骤...' :LangPack='langPack'></mdinput>
<subtitle desc='🔠反馈大于等于一个三位或四位版本号'>ℹ️你预估的受影响的Clickmouse版本</subtitle>
<ginput place='>=X.X.X 或 >=X.X.X.X'></ginput>
<subtitle desc='♻️可以提供多个Bug解决方案，但请确保每个方案都能解决你的问题。'>📄你的解决步骤想法</subtitle>
<mdinput :placeholder='idea_text' :LangPack='langPack'></mdinput>
<subtitle desc='🔄️可以提供多个Bug环节方案，但请确保每个方案都能解决你的问题。'>🔄️缓解bug的方案</subtitle>
<mdinput :placeholder='idea_text' :LangPack='langPack'></mdinput>
<subtitle desc='✉️日志位于clickmouse安装目录/cache/logs/今天日期.log中 日志段意思是以---分割的日志，请复制最后一段日志到这里。'>📂文件日志</subtitle>
<mdinput placeholder='请把文件日志的最后一段复制过来...' :LangPack='langPack'></mdinput>
<subtitle desc='✉️提供更多信息，如操作系统版本、系统语言、造成bug软件等。'>➕其他相关信息</subtitle>
<mdinput placeholder='你使用的操作系统版本、系统语言、造成bug软件等' :LangPack='langPack'></mdinput>
</strongCard>

## 功能请求

一个你建议添加的新功能。
<br />
<strongCard LabelColor='#a2eeef' TypeColor='#0969da' LabelText='enhancement' TypeText='Feature' :LangPack='{...CardLangPack, ...featureLabel}' ShowDate='true'>
<subtitle required='true' noTopMargin='true'>添加一个标题</subtitle>
<ginput text='❇️[FEATURE]'></ginput>
<note title='批注'>为避免造成更多的麻烦，请在报告issue前，先检查是否有其他人已经报告过相同的问题。<a href="https://github.com/xystudiocode/pyclickmouse/issues">检查是否存在重复</a>😊</note>
<important title='注意'>我们不会在gitee上处理issue，请使用github发布。🙋‍♂️</important>
<tip title='提示'>请一次只报告1个功能。😀</tip>
<subtitle required='true' desc='❇️你想新增功能的是什么模块？'>❇️新增功能的模块</subtitle>
<choiceBox :placeholder='ChoicePlace' multiple='true' :options='moduleOptions'></choiceBox>
<subtitle required='true' desc='📄请详细描述你想要新增的功能。'>📄新增功能描述</subtitle>
<mdinput placeholder='详细描述你想要新增的功能。' :LangPack='langPack'></mdinput>
<subtitle desc='❔为什么需要这个功能？'>❔需要这个功能的原因</subtitle>
<mdinput :placeholder='feature_reason' :LangPack='langPack'></mdinput>
<subtitle desc='♻️可以提供多个新功能实行方案，但请确保每个方案都能实行你的需求。'>🧾实行步骤想法</subtitle>
<mdinput :placeholder='idea_text' :LangPack='langPack'></mdinput>
<subtitle desc='📄你了解到的更多内容'>➕其他相关信息</subtitle>
<mdinput placeholder='更多信息。' :LangPack='langPack'></mdinput>
</strongCard>

## 新标准

将会建议，建立或修改一个标准。
<br />
<strongCard LabelColor='#a2eeef' TypeColor='#0969da' LabelText='enhancement' TypeText='Feature' :LangPack='{...CardLangPack, ...featureLabel}'>
<subtitle required='true' noTopMargin='true'>添加一个标题</subtitle>
<ginput text='🗒️[SPA]'></ginput>
<note title='批注'>为避免造成更多的麻烦，请在报告issue前，先检查是否有其他人已经报告过相同的问题。<a href="https://github.com/xystudiocode/pyclickmouse/issues">检查是否存在重复</a>😊</note>
<important title='注意'>我们不会在gitee上处理issue，请使用github发布。🙋‍♂️</important>
<tip title='提示'>请一次只报告1个立项。😀</tip>
<subtitle required='true' desc='🧾请详细描述你想要立项的标准。'>🧾新增的立项</subtitle>
<mdinput placeholder='请在这里输入立项内容。' :LangPack='langPack'></mdinput>
<subtitle required='true' desc='🔠反馈一个三位或四位版本号'>ℹ️立项施行的clickmouse版本</subtitle>
<ginput place='X.X.X 或 X.X.X.X' text='下一个clickmouse正式版'></ginput>
<subtitle desc='❓为什么需要这个立项？'>❓需要这些立项的原因</subtitle>
<mdinput :placeholder='feature_reason' :LangPack='langPack'></mdinput>
<subtitle desc='✉️你了解到的更多内容'>➕其他相关信息</subtitle>
<mdinput placeholder='更多信息。' :LangPack='langPack'></mdinput>
</strongCard>

## 任务单

一些任务单，可以用来起草新版本的规划等。
<br />
<strongCard LabelColor='#a2eeef' TypeColor='#9a6700' LabelText='enhancement' TypeText='Task' :LangPack='{...CardLangPack, ...taskLabel}'>
<subtitle required='true' noTopMargin='true'>添加一个标题</subtitle>
<ginput text='☑️[TASK]'></ginput>
<note title='批注'>为避免造成更多的麻烦，请在报告issue前，先检查是否有其他人已经报告过相同的问题。<a href="https://github.com/xystudiocode/pyclickmouse/issues">检查是否存在重复</a>😊</note>
<important title='注意'>我们不会在gitee上处理issue，请使用github发布。🙋‍♂️</important>
<subtitle required='true' desc='☑️你想新增任务包含哪些模块？'>☑️新增任务包含的模块</subtitle>
<choiceBox :placeholder='ChoicePlace' multiple='true' :options='moduleOptions'></choiceBox>
<subtitle required='true' desc='📄请详细描述你想要新增的功能。'>📄新增的每个功能描述</subtitle>
<mdinput placeholder='- 新功能1&#10;- 新功能2&#10;- 新功能3&#10;- 新功能...' :LangPack='langPack'></mdinput>
<subtitle desc='❓为什么需要这些功能？'>❓需要这些功能的原因</subtitle>
<mdinput :placeholder='feature_reason' :LangPack='langPack'></mdinput>
<subtitle desc='♻️可以提供多个新功能的多个实行方案，但请确保每个方案都能实行你的需求。'>📄实行步骤想法</subtitle>
<mdinput :placeholder='task_idea'></mdinput>
<subtitle desc='📄你了解到的更多内容'>➕其他相关信息</subtitle>
<mdinput placeholder='更多信息。' :LangPack='langPack'></mdinput>
</strongCard>
