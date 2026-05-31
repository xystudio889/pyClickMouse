---
title: issue template
description: View issue template online
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
        { value: 'official', label: '✅Yes' },
        { value: 'unofficial', label: '❌No' },
        { value: 'dontknow', label: '❓I don\'t know/forgot' }
      ],
      moduleOptions: [
        { value: 'Clicker',label: '🖱️Click function' },
        { value: 'Calculator',label: '🧮Real-time calculation and judgment of click delay (including main window, settings and fast click)' },
        { value: 'Setting',label: '⚙️Settings' },
        { value: 'Theme',label: '✳️Adaptive theme color switching' },
        { value: 'Hotkey',label: '⌨️Hotkeys' },
        { value: 'Tray',label: '️⬜Tray application' },
        { value: 'OtherMain',label: '☁️Other main program functions' },
        { value: 'Init',label: '⬇️Initialization program' },
        { value: 'PackageManager',label: '📦Package manager (including initialized package manager)' },
        { value: 'Uninstall',label: '🗑️Uninstall program' },
        { value: 'Update',label: '🔄️Check update service' },
        { value: 'Fix',label: '🔧Repair program' },
        { value: 'Install',label: '⤴️Install updates' },
        { value: 'Extension',label: '💠Other extensions' },
        { value: 'Clean',label: '♻️Clean cache' },
        { value: 'Theme/Style',label: '🏳️‍🌈Theme/Style' },
        { value: 'Document',label: '📄Documentation' },
        { value: 'clickClean',label: '🟦clickClean'},
        { value: 'Unknown',label: '❓Other/Unknown' },
      ],
      idea_text: '- Solution 1:\n- 1. Solution step 1\n- 2. Solution step 2\n- 3. Solution step 3\n- 4. Solution step ...\n- Solution 2:\n- 1. Solution step 1\n- 2. Solution step 2\n- 3. Solution step 3\n- 4. Solution step ...\n- Solution 3:\n- 1. Solution step 1\n- 2. Solution step 2\n- 3. Solution step 3\n- 4. Solution step ...\n- Solution ...',
      langPack: {
        Write: 'Write',
        Preview: 'Preview',
        More: 'More',
        H3: 'Header',
        Bold: 'Bold',
        Italic: 'Italic',
        Quote: 'Quote',
        Code: 'Code',
        Link: 'Link',
        UnOrderedList: 'Unordered List',
        NumList: 'Numbered List',
        TaskList: 'Task List',
        AddFile: 'Paste, drop or click to add files.',
        Nothing: 'Nothing to preview.',
      },
      feature_reason: 'What problem does it solve?\nWhat does it improve?\nOther reasons...',
      task_idea: `- New feature 1:\n- - Implementation plan 1:\n- - 1. Implementation step 1\n- - 2. Implementation step 2\n- - 3. Implementation step 3\n- - 4. Implementation step ...\n- - Implementation plan 2:\n- - 1. Implementation step 1\n- - 2. Implementation step 2\n- - 3. Implementation step 3\n- - 4. Implementation step ...\n- - Implementation plan 3:\n- - 1. Implementation step 1\n- - 2. Implementation step 2\n- - 3. Implementation step 3\n- - 4. Implementation step ...\n- - Other implementation plans...\n- New feature 2:\n- - Implementation plan 1:\n- - 1. Implementation step 1\n- - 2. Implementation step 2\n- - 3. Implementation step 3\n- - 4. Implementation step ...\n- - Implementation plan 2:\n- - 1. Implementation step 1\n- - 2. Implementation step 2\n- - 3. Implementation step 3\n- - 4. Implementation step ...\n- - Implementation plan 3:\n- - 1. Implementation step 1\n- - 2. Implementation step 2\n- - 3. Implementation step 3\n- - 4. Implementation step ...\n- - Other implementation plans...\n- New feature 3:\n- - Implementation plan 1:\n- - 1. Implementation step 1\n- - 2. Implementation step 2\n- - 3. Implementation step 3\n- - 4. Implementation step ...\n- - Implementation plan 2:\n- - 1. Implementation step 1\n- - 2. Implementation step 2\n- - 3. Implementation step 3\n- - 4. Implementation step ...\n- - Implementation plan 3:\n- - 1. Implementation step 1\n- - 2. Implementation step 2\n- - 3. Implementation step 3\n- - 4. Implementation step ...\n- - Other implementation plans...\n- Other features...`,
      ChoicePlace: 'None',
      CardLangPack: {
        Assignee: 'Assignee',
        LabelDesc: 'Label',
        TypeDesc: 'Issue Type',
        Project: 'Project',
        Milestone: 'Milestone',
        Product: 'Remember, contributions to this repository should follow its',
        GuideLines: 'contributing guidelines',
        Security: 'security policy',
        And: 'and',
        CreateMore: 'Create More',
        Cancel: 'Cancel',
        Create: 'Create',
        Priority: 'Priority',
        Effort: 'Effort',
        StartDate: 'Start date',
        TargetDate: 'Target date',
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

# issue template
## Bug Report
Report a bug.
<br />
<strongCard LabelColor='#d73a4a' TypeColor='#f85149' :LangPack='{...CardLangPack, ...bugLabel}'>
<subtitle required='true' noTopMargin='true'>Add a title</subtitle>
<ginput text='🐛[BUG]'></ginput>
<note title='Note'>To avoid causing more trouble, before reporting issue, first check if others have already reported same problem.<a href="https://github.com/xystudiocode/pyclickmouse/issues">Check if duplicate exists</a>😊</note>
<important title='Important'>We will not handle issues on gitee, please use github to publish.🙋‍♂️</important>
<tip title='Tip'>Please only report 1 problem at a time.😀</tip>
<subtitle required='true' desc='Feedback three or four digit version number, can go to "Help" - "About" interface view current clickmouse version number'>🔡Clickmouse version</subtitle>
<ginput text='' place='X.X.X or X.X.X.X'></ginput>
<subtitle required='true'>🎭Did you discover bug from official version</subtitle>
<p class="desc">❗clickmouse official version only published on<a href="https://github.com/xystudiocode/pyclickmouse/releases">github releases</a> or <a href="https://gitee.com/xystudiocode/pyclickmouse/releases">gitee releases</a>, others are unofficial versions.</p>
<choiceBox v-model='defaultOfficalSelect' :options='officalOptions'>
</choiceBox>
<br />
<subtitle required='true' desc='🐛Please select module where you encountered bug, can select multiple.'>🐛Module where you encountered bug</subtitle>
<choiceBox multiple='true' :options='moduleOptions'></choiceBox>
<subtitle required='true' desc='🐍Bug description'>🐍Describe your bug.</subtitle>
<mdinput placeholder='Please describe here' :LangPack='langPack'></mdinput>
<subtitle required='false' desc='🔦Describe impact of this bug.'>🔦Impact of this bug.</subtitle>
<mdinput placeholder='Please describe here' :LangPack='langPack'></mdinput>
<subtitle required='false' desc='🔧Describe how to reproduce this bug.'>📝Reproduction steps</subtitle>
<mdinput placeholder='1. Step 1&#10;2. Step 2&#10;3. Step 3&#10;4. Step ...' :LangPack='langPack'></mdinput>
<subtitle desc='🔠Feedback greater than or equal to one three or four digit version number'>ℹ️Estimated affected Clickmouse versions</subtitle>
<ginput place='>=X.X.X or >=X.X.X.X'></ginput>
<subtitle desc='♻️Can provide multiple Bug solutions, but please ensure each solution can solve your problem.'>📄Your solution step ideas</subtitle>
<mdinput :placeholder='idea_text' :LangPack='langPack'></mdinput>
<subtitle desc='🔄️Can provide multiple Bug mitigation solutions, but please ensure each solution can solve your problem.'>🔄️Bug mitigation solutions</subtitle>
<mdinput :placeholder='idea_text' :LangPack='langPack'></mdinput>
<subtitle desc='✉️Logs located at clickmouse installation directory/cache/logs/today date.log Log segment meaning is log separated by ---, please copy last segment log here.'>📂File logs</subtitle>
<mdinput placeholder='Please copy last segment of file logs here...' :LangPack='langPack'></mdinput>
<subtitle desc='✉️Provide more information, such as operating system version, system language, software causing bug, etc.'>➕Other related information</subtitle>
<mdinput placeholder='Your operating system version, system language, software causing bug, etc' :LangPack='langPack'></mdinput>
</strongCard>

## Feature Request
A new feature you suggest to add.
<br />
<strongCard LabelColor='#a2eeef' TypeColor='#0969da' :LangPack='{...CardLangPack, ...featureLabel}' :ShowDate='true'>
<subtitle required='true' noTopMargin='true'>Add a title</subtitle>
<ginput text='❇️[FEATURE]'></ginput>
<note title='Note'>To avoid causing more trouble, before reporting issue, first check if others have already reported same problem.<a href="https://github.com/xystudiocode/pyclickmouse/issues">Check if duplicate exists</a>😊</note>
<important title='Important'>We will not handle issues on gitee, please use github to publish.🙋‍♂️</important>
<tip title='Tip'>Please only report 1 feature at a time.😀</tip>
<subtitle required='true' desc='❇️What module do you want to add new feature to?'>❇️Module for new feature</subtitle>
<choiceBox multiple='true' :options='moduleOptions'></choiceBox>
<subtitle required='true' desc='📄Please describe in detail the new feature you want to add.'>📄New feature description</subtitle>
<mdinput placeholder='Describe in detail the new feature you want to add.' :LangPack='langPack'></mdinput>
<subtitle desc='❔Why is this feature needed?'>❔Reason for needing this feature</subtitle>
<mdinput :placeholder='feature_reason' :LangPack='langPack'></mdinput>
<subtitle desc='♻️Can provide multiple new feature implementation solutions, but please ensure each solution can implement your requirements.'>🧾Implementation step ideas</subtitle>
<mdinput :placeholder='idea_text' :LangPack='langPack'></mdinput>
<subtitle desc='📄More content you understand'>➕Other related information</subtitle>
<mdinput placeholder='More information.' :LangPack='langPack'></mdinput>
</strongCard>

## New Standard
Will suggest, establish or modify a standard.
<br />
<strongCard LabelColor='#a2eeef' TypeColor='#0969da' :LangPack='{...CardLangPack, ...featureLabel}'>
<subtitle required='true' noTopMargin='true'>Add a title</subtitle>
<ginput text='🗒️[SPA]'></ginput>
<note title='Note'>To avoid causing more trouble, before reporting issue, first check if others have already reported same problem.<a href="https://github.com/xystudiocode/pyclickmouse/issues">Check if duplicate exists</a>😊</note>
<important title='Important'>We will not handle issues on gitee, please use github to publish.🙋‍♂️</important>
<tip title='Tip'>Please only report 1 project at a time.😀</tip>
<subtitle required='true' desc='🧾Please describe in detail the standard you want to establish.'>🧾New project</subtitle>
<mdinput placeholder='Please enter project content here.' :LangPack='langPack'></mdinput>
<subtitle required='true' desc='🔠Feedback a three or four digit version number'>ℹ️Clickmouse version for project implementation</subtitle>
<ginput place='X.X.X or X.X.X.X' text='Next clickmouse official version'></ginput>
<subtitle desc='❓Why is this project needed?'>❓Reason for needing these projects</subtitle>
<mdinput :placeholder='feature_reason' :LangPack='langPack'></mdinput>
<subtitle desc='✉️More content you understand'>➕Other related information</subtitle>
<mdinput placeholder='More information.' :LangPack='langPack'></mdinput>
</strongCard>

## Task Order
Some task orders, can be used to draft new version planning, etc.
<br />
<strongCard LabelColor='#a2eeef' TypeColor='#9a6700' :LangPack='{...CardLangPack, ...taskLabel}'>
<subtitle required='true' noTopMargin='true'>Add a title</subtitle>
<ginput text='☑️[TASK]'></ginput>
<note title='Note'>To avoid causing more trouble, before reporting issue, first check if others have already reported same problem.<a href="https://github.com/xystudiocode/pyclickmouse/issues">Check if duplicate exists</a>😊</note>
<important title='Important'>We will not handle issues on gitee, please use github to publish.🙋‍♂️</important>
<subtitle required='true' desc='☑️What modules do you want new task to include?'>☑️Modules included in new task</subtitle>
<choiceBox multiple='true' :options='moduleOptions'></choiceBox>
<subtitle required='true' desc='📄Please describe in detail each new feature you want to add.'>📄Description of each new feature</subtitle>
<mdinput placeholder='- New feature 1&#10;- New feature 2&#10;- New feature 3&#10;- New feature ...' :LangPack='langPack'></mdinput>
<subtitle desc='❓Why are these features needed?'>❓Reason for needing these features</subtitle>
<mdinput :placeholder='feature_reason' :LangPack='langPack'></mdinput>
<subtitle desc='♻️Can provide multiple implementation solutions for multiple new features, but please ensure each solution can implement your requirements.'>📄Implementation step ideas</subtitle>
<mdinput :placeholder='task_idea'></mdinput>
<subtitle desc='📄More content you understand'>➕Other related information</subtitle>
<mdinput placeholder='More information.' :LangPack='langPack'></mdinput>
</strongCard>