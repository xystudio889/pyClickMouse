<template>
  <div
    class="mdinput"
    :class="{ 'has-content': markdownText && markdownText.trim() !== '' }"
    ref="menu"
  >
    <div class="menu">
      <nav class="tabs" ref="tabs">
        <button
          class="tabItem"
          :class="{
            active: activeTab === 'write',
            focused: rovingScope === 'tabs' && rovingVisible && tabRovingIndex === 0
          }"
          @click="handleTabClick(0)"
        >
          {{ LangPack.Write ?? 'Write' }}
        </button>
        <button
          class="tabItem"
          :class="{
            active: activeTab === 'preview',
            focused: rovingScope === 'tabs' && rovingVisible && tabRovingIndex === 1
          }"
          @click="handleTabClick(1)"
        >
          {{ LangPack.Preview ?? 'Preview' }}
        </button>
      </nav>

      <!-- 工具栏仅在 Write 标签下显示 -->
      <div class="tools" v-show="activeTab === 'write'">
        <template v-for="(item, index) in visibleItems" :key="index">
          <button
            v-if="item.type === 'button'"
            type="button"
            class="tool-button"
            :class="{
              focused: rovingScope === 'toolbar' && rovingVisible && toolRovingIndex === getToolButtonIndex(index)
            }"
            v-html="item.icon"
            @click="handleToolClick(item, index)"
            :data-tooltip="item.name"
          ></button>
          <div v-else-if="item.type === 'divider'" class="splitLine"></div>
        </template>

        <button
          v-if="showDotsButton"
          type="button"
          class="tool-button dots-button"
          :class="{
            focused: rovingScope === 'toolbar' && rovingVisible && toolRovingIndex === totalToolItems - 1
          }"
          ref="dotsButton"
          tabindex="0"
          @click="handleDotsClick"
          @keydown.enter="handleDotsKeydown"
          @keydown.space="handleDotsKeydown"
          :data-tooltip="LangPack.More ?? 'More'"
        >
          <svg viewBox="0 0 16 16" width="16" height="16" class="item-svg">
            <path d="M8 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3ZM1.5 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Zm13 0a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z" />
          </svg>
        </button>

        <ul
          v-show="menuOpen && foldedItems.length > 0"
          class="dots-dropdown"
          ref="dropdown"
        >
          <li
            v-for="(item, idx) in foldedItems"
            :key="idx"
            class="dropdown-item"
            :class="{
              divider: item.type === 'divider',
              focused: focusVisible && focusedIndex === idx && item.type === 'button'
            }"
            @click="handleMenuItemClick(item)"
          >
            <span v-if="item.type === 'button'" class="item-content">
              <span class="item-icon" v-html="item.icon"></span>
              <span class="item-name">{{ item.name }}</span>
            </span>
            <hr v-else class="dropdown-divider" />
          </li>
        </ul>
      </div>
    </div>

    <textarea
      v-if="activeTab === 'write'"
      ref="textarea"
      class="mdTextArea"
      :placeholder="placeholder"
      v-model="markdownText"
      @keydown.enter.prevent="handleEnter"
    ></textarea>

    <div
      v-else
      class="mdPreview"
      v-html="renderedHtml"
    ></div>
  </div>
  <div class="bottom-addFile">
    <button class="file-Btn">
      <span>
      <svg aria-hidden="true" focusable="false" viewBox="0 0 16 16" width="16" height="16" fill="currentColor" display="inline-block" overflow="visible" style="vertical-align: text-bottom;"><path d="M12.212 3.02a1.753 1.753 0 0 0-2.478.003l-5.83 5.83a3.007 3.007 0 0 0-.88 2.127c0 .795.315 1.551.88 2.116.567.567 1.333.89 2.126.89.79 0 1.548-.321 2.116-.89l5.48-5.48a.75.75 0 0 1 1.061 1.06l-5.48 5.48a4.492 4.492 0 0 1-3.177 1.33c-1.2 0-2.345-.487-3.187-1.33a4.483 4.483 0 0 1-1.32-3.177c0-1.195.475-2.341 1.32-3.186l5.83-5.83a3.25 3.25 0 0 1 5.553 2.297c0 .863-.343 1.691-.953 2.301L7.439 12.39c-.375.377-.884.59-1.416.593a1.998 1.998 0 0 1-1.412-.593 1.992 1.992 0 0 1 0-2.828l5.48-5.48a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-5.48 5.48a.492.492 0 0 0 0 .707.499.499 0 0 0 .352.154.51.51 0 0 0 .356-.154l5.833-5.827a1.755 1.755 0 0 0 0-2.481Z"></path></svg>
      {{ LangPack.AddFile ?? 'Paste, drop or click to add files' }}
      </span>
    </button>
  </div>
</template>

<script>
import { marked } from 'marked';

export default {
  name: 'MdInput',
  props: {
    LangPack: { type: Object, default: () => ({}) },
    placeholder: { type: String, default: '' },
    value: { type: String, default: '' },
  },
  data() {
    return {
      activeTab: 'write',
      foldedIndex: Infinity,
      menuOpen: false,
      observer: null,
      markdownText: this.value,
      focusedIndex: 0,
      focusVisible: false,
      rovingScope: null,
      tabRovingIndex: 0,
      toolRovingIndex: 0,
      rovingVisible: false,
    };
  },
  computed: {
    items() {
      return [
        { type: 'button', id: 'h3', name: this.LangPack.H3 ?? 'Title', icon: '<svg class="item-svg" viewBox="0 0 16 16" width="16" height="16"><path d="M3.75 2a.75.75 0 0 1 .75.75V7h7V2.75a.75.75 0 0 1 1.5 0v10.5a.75.75 0 0 1-1.5 0V8.5h-7v4.75a.75.75 0 0 1-1.5 0V2.75A.75.75 0 0 1 3.75 2Z"></path></svg>' },
        { type: 'button', id: 'bold', name: this.LangPack.Bold ?? 'Bold', icon: '<svg class="item-svg" viewBox="0 0 16 16" width="16" height="16"><path d="M4 2h4.5a3.501 3.501 0 0 1 2.852 5.53A3.499 3.499 0 0 1 9.5 14H4a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1Zm1 7v3h4.5a1.5 1.5 0 0 0 0-3Zm3.5-2a1.5 1.5 0 0 0 0-3H5v3Z"></path></svg>' },
        { type: 'button', id: 'italic', name: this.LangPack.Italic ?? 'Italic', icon: '<svg class="item-svg" viewBox="0 0 16 16" width="16" height="16"><path d="M6 2.75A.75.75 0 0 1 6.75 2h6.5a.75.75 0 0 1 0 1.5h-2.505l-3.858 9H9.25a.75.75 0 0 1 0 1.5h-6.5a.75.75 0 0 1 0-1.5h2.505l3.858-9H6.75A.75.75 0 0 1 6 2.75Z"></path></svg>' },
        { type: 'button', id: 'quote', name: this.LangPack.Quote ?? 'Quote', icon: '<svg class="item-svg" viewBox="0 0 16 16" width="16" height="16"><path d="M1.75 2.5h10.5a.75.75 0 0 1 0 1.5H1.75a.75.75 0 0 1 0-1.5Zm4 5h8.5a.75.75 0 0 1 0 1.5h-8.5a.75.75 0 0 1 0-1.5Zm0 5h8.5a.75.75 0 0 1 0 1.5h-8.5a.75.75 0 0 1 0-1.5ZM2.5 7.75v6a.75.75 0 0 1-1.5 0v-6a.75.75 0 0 1 1.5 0Z"></path></svg>' },
        { type: 'button', id: 'code', name: this.LangPack.Code ?? 'Code', icon: '<svg class="item-svg" viewBox="0 0 16 16" width="16" height="16"><path d="m11.28 3.22 4.25 4.25a.75.75 0 0 1 0 1.06l-4.25 4.25a.749.749 0 0 1-1.275-.326.749.749 0 0 1 .215-.734L13.94 8l-3.72-3.72a.749.749 0 0 1 .326-1.275.749.749 0 0 1 .734.215Zm-6.56 0a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042L2.06 8l3.72 3.72a.749.749 0 0 1-.326 1.275.749.749 0 0 1-.734-.215L.47 8.53a.75.75 0 0 1 0-1.06Z"></path></svg>' },
        { type: 'button', id: 'link', name: this.LangPack.Link ?? 'Link', icon: '<svg class="item-svg" viewBox="0 0 16 16" width="16" height="16"><path d="m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z"></path></svg>' },
        { type: 'divider' },
        { type: 'button', id: 'ul', name: this.LangPack.UnOrderedList ?? 'Unorderd List', icon: '<svg class="item-svg" viewBox="0 0 16 16" width="16" height="16"><path d="M5.75 2.5h8.5a.75.75 0 0 1 0 1.5h-8.5a.75.75 0 0 1 0-1.5Zm0 5h8.5a.75.75 0 0 1 0 1.5h-8.5a.75.75 0 0 1 0-1.5Zm0 5h8.5a.75.75 0 0 1 0 1.5h-8.5a.75.75 0 0 1 0-1.5ZM2 14a1 1 0 1 1 0-2 1 1 0 0 1 0 2Zm1-6a1 1 0 1 1-2 0 1 1 0 0 1 2 0ZM2 4a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z"></path></svg>' },
        { type: 'button', id: 'ol', name: this.LangPack.NumList ?? 'Numbered List', icon: '<svg class="item-svg" viewBox="0 0 16 16" width="16" height="16"><path d="M5 3.25a.75.75 0 0 1 .75-.75h8.5a.75.75 0 0 1 0 1.5h-8.5A.75.75 0 0 1 5 3.25Zm0 5a.75.75 0 0 1 .75-.75h8.5a.75.75 0 0 1 0 1.5h-8.5A.75.75 0 0 1 5 8.25Zm0 5a.75.75 0 0 1 .75-.75h8.5a.75.75 0 0 1 0 1.5h-8.5a.75.75 0 0 1-.75-.75ZM.924 10.32a.5.5 0 0 1-.851-.525l.001-.001.001-.002.002-.004.007-.011c.097-.144.215-.273.348-.384.228-.19.588-.392 1.068-.392.468 0 .858.181 1.126.484.259.294.377.673.377 1.038 0 .987-.686 1.495-1.156 1.845l-.047.035c-.303.225-.522.4-.654.597h1.357a.5.5 0 0 1 0 1H.5a.5.5 0 0 1-.5-.5c0-1.005.692-1.52 1.167-1.875l.035-.025c.531-.396.8-.625.8-1.078a.57.57 0 0 0-.128-.376C1.806 10.068 1.695 10 1.5 10a.658.658 0 0 0-.429.163.835.835 0 0 0-.144.153ZM2.003 2.5V6h.503a.5.5 0 0 1 0 1H.5a.5.5 0 0 1 0-1h.503V3.308l-.28.14a.5.5 0 0 1-.446-.895l1.003-.5a.5.5 0 0 1 .723.447Z"></path></svg>' },
        { type: 'button', id: 'task', name: this.LangPack.TaskList ?? 'Task List', icon: '<svg class="item-svg" viewBox="0 0 16 16" width="16" height="16"><path d="M2 2h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1Zm4.655 8.595a.75.75 0 0 1 0 1.06L4.03 14.28a.75.75 0 0 1-1.06 0l-1.5-1.5a.749.749 0 0 1 .326-1.275.749.749 0 0 1 .734.215l.97.97 2.095-2.095a.75.75 0 0 1 1.06 0ZM9.75 2.5h5.5a.75.75 0 0 1 0 1.5h-5.5a.75.75 0 0 1 0-1.5Zm0 5h5.5a.75.75 0 0 1 0 1.5h-5.5a.75.75 0 0 1 0-1.5Zm0 5h5.5a.75.75 0 0 1 0 1.5h-5.5a.75.75 0 0 1 0-1.5Zm-7.25-9v3h3v-3Z"></path></svg>' },
      ];
    },
    visibleItems() {
      return this.items.slice(0, this.foldedIndex);
    },
    foldedItems() {
      return this.items.slice(this.foldedIndex);
    },
    showDotsButton() {
      return this.foldedItems.length > 0;
    },
    renderedHtml() {
      if (!this.markdownText) return `<p>${this.LangPack.Nothing ?? 'Nothing to Preview.'}</p>`;
      try {
        return marked(this.markdownText, { gfm: true, breaks: true });
      } catch (e) {
        console.error('Markdown 解析失败', e);
        return '<p style="color:red">解析错误</p>';
      }
    },
    totalToolItems() {
      const visibleButtons = this.visibleItems.filter(item => item.type === 'button').length;
      return visibleButtons + (this.showDotsButton ? 1 : 0);
    },
  },
  watch: {
    // 折叠变化后的焦点重定位
    foldedItems: {
      handler(newVal, oldVal) {
        if (newVal.length === 0) this.menuOpen = false;

        if (this.menuOpen && this.focusVisible) {
          if (newVal.length === 0) {
            this.focusVisible = false;
            return;
          }
          if (this.focusedIndex >= newVal.length || newVal[this.focusedIndex].type !== 'button') {
            this.focusedIndex = this.getFirstFocusableIndex();
            this.$nextTick(() => this.scrollFocusedIntoView());
          }
        }

        this.$nextTick(() => {
          if (this.rovingScope !== 'toolbar' || this.totalToolItems === 0) return;

          const currentItem = this.getToolItemByIndex(this.toolRovingIndex);
          let newIndex = 0;

          if (currentItem) {
            if (currentItem.type === 'button') {
              const id = currentItem.item.id;
              let foundInVisible = false;
              let btnCount = 0;
              for (let i = 0; i < this.visibleItems.length; i++) {
                if (this.visibleItems[i].type === 'button') {
                  if (this.visibleItems[i].id === id) {
                    foundInVisible = true;
                    newIndex = btnCount;
                    break;
                  }
                  btnCount++;
                }
              }
              if (!foundInVisible) {
                newIndex = this.showDotsButton ? this.totalToolItems - 1 : 0;
              }
            } else if (currentItem.type === 'dots') {
              newIndex = this.showDotsButton ? this.totalToolItems - 1 : 0;
            }
          } else {
            newIndex = 0;
          }

          newIndex = Math.min(Math.max(0, newIndex), this.totalToolItems - 1);
          if (newIndex !== this.toolRovingIndex) {
            this.toolRovingIndex = newIndex;
          }
          if (this.rovingVisible && this.rovingScope === 'toolbar') {
            this.$nextTick(() => {
              this.focusToolItemByIndex(this.toolRovingIndex);
            });
          }
        });
      },
      deep: false,
    },
    markdownText(newVal) {
      this.$emit('input', newVal);
    },
    value(newVal) {
      this.markdownText = newVal;
    },
    // 切换标签时，若回到 Write 则重新计算折叠
    activeTab(newVal) {
      if (newVal === 'write') {
        this.$nextTick(() => {
          this.calculateFold();
        });
      }
    },
  },
  mounted() {
    this.calculateFold();

    if (window.ResizeObserver) {
      this.observer = new ResizeObserver(() => {
        // 仅在 Write 标签下计算折叠，避免影响 Preview
        if (this.activeTab === 'write') {
          this.calculateFold();
        }
      });
      if (this.$refs.menu) {
        this.observer.observe(this.$refs.menu);
      }
    } else {
      window.addEventListener('resize', this.calculateFold);
    }

    document.addEventListener('click', this.handleClickOutside);
    document.addEventListener('keydown', this.handleDocumentKeyDown);
  },
  beforeUnmount() {
    if (this.observer) {
      this.observer.disconnect();
    } else {
      window.removeEventListener('resize', this.calculateFold);
    }
    document.removeEventListener('click', this.handleClickOutside);
    document.removeEventListener('keydown', this.handleDocumentKeyDown);
  },
  methods: {
    calculateFold() {
      const menuEl = this.$refs.menu;
      const tabsEl = this.$refs.tabs;
      if (!menuEl || !tabsEl) return;

      const menuWidth = menuEl.getBoundingClientRect().width;
      const tabsWidth = tabsEl.getBoundingClientRect().width;

      const getItemWidth = (item) => (item.type === 'divider' ? 17 : 32);
      const allItemsWidth = this.items.reduce((sum, item) => sum + getItemWidth(item), 0);
      const dotsWidth = 32;

      const totalToolsWidth = allItemsWidth + dotsWidth;
      let remaining = menuWidth - tabsWidth - totalToolsWidth;

      if (remaining >= 50) {
        this.foldedIndex = this.items.length;
        return;
      }

      let need = 50 - remaining;
      let foldedWidth = 0;
      let newIndex = this.items.length;

      for (let i = this.items.length - 1; i >= 0; i--) {
        foldedWidth += getItemWidth(this.items[i]);
        if (foldedWidth >= need) {
          newIndex = i;
          break;
        }
      }

      this.foldedIndex = newIndex;
    },

    // ==================== 工具栏功能实现 ====================
    handleToolAction(item) {
      if (!item || item.type !== 'button') return;
      switch (item.id) {
        case 'h3': this.handleTitle(); break;
        case 'bold': this.handleBold(); break;
        case 'italic': this.handleItalic(); break;
        case 'quote': this.handleQuote(); break;
        case 'code': this.handleCode(); break;
        case 'link': this.handleLink(); break;
        case 'ul': this.handleUnorderedList(); break;
        case 'ol': this.handleOrderedList(); break;
        case 'task': this.handleTaskList(); break;
        default: console.log('Unknown tool:', item.name);
      }
    },

    // 标题：在光标处插入 "### "（无智能删除，直接插入）
    handleTitle() {
      const ta = this.$refs.textarea;
      if (!ta) return;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const text = this.markdownText;
      const left = text.substring(0, start);
      const right = text.substring(end);
      const insert = '### ';
      this.markdownText = left + insert + right;
      this.$nextTick(() => {
        ta.focus();
        const pos = start + insert.length;
        ta.setSelectionRange(pos, pos);
      });
    },

    // 粗体：** 包裹或移除
    handleBold() {
      this.togglePair('**', '**');
    },

    // 斜体：_ 包裹或移除
    handleItalic() {
      this.togglePair('_', '_');
    },

    // 行内代码：` 包裹或移除
    handleCode() {
      this.togglePair('`', '`');
    },

    // 通用包裹/移除逻辑（用于对称标记如 **, _, `）
    togglePair(leftMark, rightMark) {
      const ta = this.$refs.textarea;
      if (!ta) return;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const text = this.markdownText;
      const selected = text.substring(start, end);
      const left = text.substring(0, start);
      const right = text.substring(end);

      // 情况1：有选区且选区已由标记完全包裹（包括标记） -> 去除包裹
      if (selected.startsWith(leftMark) && selected.endsWith(rightMark) && selected.length >= leftMark.length + rightMark.length) {
        const inner = selected.substring(leftMark.length, selected.length - rightMark.length);
        this.markdownText = left + inner + right;
        this.$nextTick(() => {
          ta.focus();
          ta.setSelectionRange(start, start + inner.length);
        });
        return;
      }

      // 情况2：无选区且光标正好位于一对标记中间（左右紧邻标记） -> 移除这对标记
      if (start === end) {
        const leftTwo = left.slice(-leftMark.length);
        const rightTwo = right.slice(0, rightMark.length);
        if (leftTwo === leftMark && rightTwo === rightMark) {
          const newLeft = left.slice(0, -leftMark.length);
          const newRight = right.slice(rightMark.length);
          this.markdownText = newLeft + newRight;
          this.$nextTick(() => {
            ta.focus();
            const pos = newLeft.length;
            ta.setSelectionRange(pos, pos);
          });
          return;
        }
      }

      // 默认：添加包裹
      const newText = left + leftMark + selected + rightMark + right;
      this.markdownText = newText;
      this.$nextTick(() => {
        ta.focus();
        if (selected) {
          // 选中原本的内容（不包括标记）
          ta.setSelectionRange(start + leftMark.length, start + leftMark.length + selected.length);
        } else {
          // 无选区，光标放在两个标记中间
          const pos = start + leftMark.length;
          ta.setSelectionRange(pos, pos);
        }
      });
    },

    // 引用：换三行，第二行为 "> "，光标位于 "> " 之后
    handleQuote() {
      const ta = this.$refs.textarea;
      if (!ta) return;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const text = this.markdownText;
      const left = text.substring(0, start);
      const right = text.substring(end);
      const insert = '\n> \n';  // 三行：第一行空，第二行 "> "，第三行空
      this.markdownText = left + insert + right;
      this.$nextTick(() => {
        ta.focus();
        // 光标位于第二行 "> " 之后，即 left.length + 1 (第一个\n) + 2 ("> ") = left.length + 3
        const pos = left.length + 3;
        ta.setSelectionRange(pos, pos);
      });
    },

    // 无序列表：切换当前行的无序标记 '- '
    handleUnorderedList() {
      this.toggleListMarker('unordered');
    },

    // 有序列表：切换当前行的有序标记 '1. '
    handleOrderedList() {
      this.toggleListMarker('ordered');
    },

    // 通用列表切换：type = 'unordered' 或 'ordered'
    toggleListMarker(type) {
      const ta = this.$refs.textarea;
      if (!ta) return;
      const value = this.markdownText;
      const start = ta.selectionStart;

      // 定位当前行
      const lineStart = value.lastIndexOf('\n', start - 1) + 1;
      let lineEnd = value.indexOf('\n', start);
      if (lineEnd === -1) lineEnd = value.length;
      const line = value.substring(lineStart, lineEnd);
      const { indent, markers, content } = this.parseLine(line);

      let newLine;
      const targetMarker = type === 'unordered' ? '- ' : '1. ';

      // 如果第一个标记已经是目标类型，则移除它；否则替换为目标的标记
      if (markers.length > 0 && markers[0].type === type) {
        // 移除标记
        newLine = indent + content;
      } else {
        // 替换/添加标记（忽略原有的所有标记）
        newLine = indent + targetMarker + content;
      }

      this.markdownText = value.substring(0, lineStart) + newLine + value.substring(lineEnd);
      this.$nextTick(() => {
        ta.focus();
        const newPos = lineStart + newLine.length;
        ta.setSelectionRange(newPos, newPos);
      });
    },

    // 任务列表：根据选区生成三行，第二行为 '- [ ] 内容'，光标位于内容后
    handleTaskList() {
      const ta = this.$refs.textarea;
      if (!ta) return;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const text = this.markdownText;
      const left = text.substring(0, start);
      const right = text.substring(end);
      const selected = text.substring(start, end);

      // 构建插入内容：无论有无选区，都产生三行，第二行是任务标记 + 内容
      // 如果无选区，selected = ''，则生成空任务项
      const insert = '\n- [ ] ' + selected + '\n';
      this.markdownText = left + insert + right;
      this.$nextTick(() => {
        ta.focus();
        // 光标放在内容后面（即 left + '\n- [ ] ' 之后 + 内容长度）
        const prefix = left + '\n- [ ] ';
        const pos = prefix.length + selected.length;
        ta.setSelectionRange(pos, pos);
      });
    },

    // 链接：将选中文本（或整行）转为 [文本](url) 并选中 url
    handleLink() {
      const ta = this.$refs.textarea;
      if (!ta) return;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const text = this.markdownText;
      const left = text.substring(0, start);
      const right = text.substring(end);
      let selected = text.substring(start, end);

      // 如果没有选区，则取光标所在行的内容（去除换行）作为选中文本
      if (!selected) {
        const lineStart = text.lastIndexOf('\n', start - 1) + 1;
        let lineEnd = text.indexOf('\n', start);
        if (lineEnd === -1) lineEnd = text.length;
        selected = text.substring(lineStart, lineEnd).trim(); // 简单取整行并trim
      }

      const insert = '[' + selected + '](url)';
      this.markdownText = left + insert + right;
      this.$nextTick(() => {
        ta.focus();
        // 选中 "url" 这三个字符（位于 ]( 之后）
        const urlStart = left.length + insert.indexOf('url');
        const urlEnd = urlStart + 3;
        ta.setSelectionRange(urlStart, urlEnd);
      });
    },

    // 原有工具方法，用于菜单项点击
    handleMenuItemClick(item) {
      if (item.type === 'button') {
        this.handleToolAction(item);
      }
      this.closeMenu('item-click');
    },

    getToolButtonIndex(visibleIndex) {
      let count = 0;
      for (let i = 0; i < this.visibleItems.length; i++) {
        if (this.visibleItems[i].type === 'button') {
          if (i === visibleIndex) return count;
          count++;
        }
      }
      return count;
    },

    getToolItemByIndex(index) {
      if (index < 0 || index >= this.totalToolItems) return null;
      let buttonCount = 0;
      for (let i = 0; i < this.visibleItems.length; i++) {
        if (this.visibleItems[i].type === 'button') {
          if (buttonCount === index) {
            return { type: 'button', item: this.visibleItems[i] };
          }
          buttonCount++;
        }
      }
      if (this.showDotsButton && buttonCount === index) {
        return { type: 'dots' };
      }
      return null;
    },

    // 新增：根据索引聚焦工具栏按钮
    focusToolItemByIndex(index) {
      if (index < 0 || index >= this.totalToolItems) return;
      let buttonCount = 0;
      const buttons = this.$el.querySelectorAll('.tool-button:not(.dots-button)');
      for (let i = 0; i < buttons.length; i++) {
        if (buttonCount === index) {
          buttons[i].focus();
          return;
        }
        buttonCount++;
      }
      if (this.showDotsButton && buttonCount === index) {
        this.$refs.dotsButton?.focus();
      }
    },

    setRovingFocus(scope, index, visible = true) {
      this.rovingScope = scope;
      if (scope === 'tabs') {
        this.tabRovingIndex = Math.min(1, Math.max(0, index));
      } else if (scope === 'toolbar') {
        const maxIndex = this.totalToolItems - 1;
        this.toolRovingIndex = Math.min(maxIndex, Math.max(0, index));
      }
      this.rovingVisible = visible;
    },

    handleTabClick(index) {
      this.setRovingFocus('tabs', index, false);
      this.activeTab = index === 0 ? 'write' : 'preview';
      // 切换标签时关闭下拉菜单
      if (this.menuOpen) {
        this.closeMenu('tab-switch');
      }
    },

    handleToolClick(item, visibleIndex) {
      const toolIndex = this.getToolButtonIndex(visibleIndex);
      this.setRovingFocus('toolbar', toolIndex, false);
      this.handleToolAction(item);
    },

    handleDotsClick() {
      const dotsIndex = this.totalToolItems - 1;
      this.setRovingFocus('toolbar', dotsIndex, false);
      this.toggleMenu(false);
    },

    openMenu(keyboardTriggered) {
      if (this.foldedItems.length === 0) return;
      this.menuOpen = true;
      this.focusVisible = keyboardTriggered;
      this.focusedIndex = this.getFirstFocusableIndex();
      if (keyboardTriggered) {
        this.$nextTick(() => {
          this.scrollFocusedIntoView();
        });
      }
      this.rovingVisible = false;
    },

    closeMenu(source) {
      this.menuOpen = false;
      this.focusVisible = false;
      this.focusedIndex = 0;

      if (source === 'escape' || source === 'item-click') {
        const dotsIndex = this.totalToolItems - 1;
        this.setRovingFocus('toolbar', dotsIndex, true);
        this.$nextTick(() => {
          if (this.$refs.dotsButton) {
            this.$refs.dotsButton.focus();
          }
        });
      } else {
        // 其他情况（如 tab-switch, outside）不聚焦
        this.rovingVisible = false;
      }
    },

    toggleMenu(keyboardTriggered = false) {
      if (this.menuOpen) {
        this.closeMenu(keyboardTriggered ? 'escape' : 'outside');
      } else {
        this.openMenu(keyboardTriggered);
      }
    },

    handleDotsKeydown(event) {
      event.preventDefault();
      if (!this.menuOpen) {
        event.stopPropagation();
        this.toggleMenu(true);
      }
    },

    handleDocumentKeyDown(event) {
      const key = event.key;

      if (this.menuOpen) {
        this.handleMenuKeyDown(event);
        return;
      }

      const activeEl = document.activeElement;
      if (activeEl === this.$refs.textarea) return;

      const isLeft = key === 'ArrowLeft';
      const isRight = key === 'ArrowRight';
      const isEnter = key === 'Enter';

      if (!this.rovingScope) return;

      if (isLeft || isRight) {
        event.preventDefault();
        if (this.rovingScope === 'tabs') {
          let newIndex = this.tabRovingIndex + (isLeft ? -1 : 1);
          if (newIndex < 0) newIndex = 1;
          if (newIndex > 1) newIndex = 0;
          this.setRovingFocus('tabs', newIndex, true);
        } else if (this.rovingScope === 'toolbar') {
          let newIndex = this.toolRovingIndex + (isLeft ? -1 : 1);
          if (newIndex < 0) newIndex = this.totalToolItems - 1;
          if (newIndex >= this.totalToolItems) newIndex = 0;
          this.setRovingFocus('toolbar', newIndex, true);
        }
      }

      if (isEnter) {
        event.preventDefault();
        if (!this.rovingVisible) return;

        if (this.rovingScope === 'tabs') {
          this.activeTab = this.tabRovingIndex === 0 ? 'write' : 'preview';
          this.rovingVisible = false;
        } else if (this.rovingScope === 'toolbar') {
          const item = this.getToolItemByIndex(this.toolRovingIndex);
          if (item) {
            if (item.type === 'button') {
              this.handleToolAction(item.item);
            } else if (item.type === 'dots') {
              this.toggleMenu(true);
            }
          }
          this.rovingVisible = false;
        }
      }
    },

    handleMenuKeyDown(event) {
      const key = event.key;

      if (key === 'ArrowLeft' || key === 'ArrowRight') {
        event.preventDefault();
        return;
      }

      const items = this.foldedItems;
      if (items.length === 0) return;

      if (['ArrowDown', 'ArrowUp', 'Enter', 'Escape', 'Home', 'End'].includes(key)) {
        event.preventDefault();
      }

      if (key === 'Escape') {
        this.closeMenu('escape');
        return;
      }

      if (key === 'Enter') {
        if (this.focusVisible) {
          const currentItem = items[this.focusedIndex];
          if (currentItem && currentItem.type === 'button') {
            this.handleMenuItemClick(currentItem);
          }
        } else {
          const first = this.getFirstFocusableIndex();
          const item = items[first];
          if (item && item.type === 'button') {
            this.handleMenuItemClick(item);
          }
        }
        return;
      }

      if (key === 'ArrowDown' || key === 'ArrowUp') {
        if (!this.focusVisible) {
          this.focusVisible = true;
          if (key === 'ArrowDown') {
            const first = this.getFirstFocusableIndex();
            this.focusedIndex = this.getNextFocusableIndex(first);
          } else {
            this.focusedIndex = this.getLastFocusableIndex();
          }
        } else {
          if (key === 'ArrowDown') {
            this.focusedIndex = this.getNextFocusableIndex(this.focusedIndex);
          } else {
            this.focusedIndex = this.getPrevFocusableIndex(this.focusedIndex);
          }
        }
        this.$nextTick(() => this.scrollFocusedIntoView());
        return;
      }

      if (key === 'Home') {
        this.focusVisible = true;
        this.focusedIndex = this.getFirstFocusableIndex();
        this.$nextTick(() => this.scrollFocusedIntoView());
      } else if (key === 'End') {
        this.focusVisible = true;
        this.focusedIndex = this.getLastFocusableIndex();
        this.$nextTick(() => this.scrollFocusedIntoView());
      }
    },

    getFirstFocusableIndex() {
      const index = this.foldedItems.findIndex(item => item.type === 'button');
      return index !== -1 ? index : 0;
    },

    getLastFocusableIndex() {
      for (let i = this.foldedItems.length - 1; i >= 0; i--) {
        if (this.foldedItems[i].type === 'button') {
          return i;
        }
      }
      return 0;
    },

    getNextFocusableIndex(currentIndex) {
      const items = this.foldedItems;
      const total = items.length;
      for (let i = 1; i <= total; i++) {
        const next = (currentIndex + i) % total;
        if (items[next].type === 'button') return next;
      }
      return currentIndex;
    },

    getPrevFocusableIndex(currentIndex) {
      const items = this.foldedItems;
      const total = items.length;
      for (let i = 1; i <= total; i++) {
        const prev = (currentIndex - i + total) % total;
        if (items[prev].type === 'button') return prev;
      }
      return currentIndex;
    },

    scrollFocusedIntoView() {
      if (!this.menuOpen || !this.focusVisible) return;
      const dropdown = this.$refs.dropdown;
      if (!dropdown) return;
      const optionElements = dropdown.querySelectorAll('.dropdown-item');
      const target = optionElements[this.focusedIndex];
      if (target) {
        target.scrollIntoView({ block: 'nearest', behavior: 'auto' });
      }
    },

    handleClickOutside(event) {
      const dotsBtn = this.$refs.dotsButton;
      const dropdown = this.$refs.dropdown;
      if (
        this.menuOpen &&
        dotsBtn &&
        !dotsBtn.contains(event.target) &&
        dropdown &&
        !dropdown.contains(event.target)
      ) {
        this.closeMenu('outside');
      }
    },

    // 智能补全相关方法（原有）
    parseLine(line) {
      const indentMatch = line.match(/^(\s*)/);
      const indent = indentMatch[1];
      let rest = line.slice(indent.length);
      const markers = [];

      const patterns = [
        { type: 'task', regex: /^\[([ x])\] / },
        { type: 'ordered', regex: /^(\d+)\. / },
        { type: 'unordered', regex: /^[-*+] / }
      ];

      while (rest.length > 0) {
        let matched = false;
        for (let p of patterns) {
          const m = rest.match(p.regex);
          if (m) {
            if (p.type === 'task') {
              markers.push({ type: 'task', value: m[1] });
            } else if (p.type === 'ordered') {
              markers.push({ type: 'ordered', value: parseInt(m[1], 10) });
            } else {
              markers.push({ type: 'unordered', value: null });
            }
            rest = rest.slice(m[0].length);
            matched = true;
            break;
          }
        }
        if (!matched) break;
      }

      const content = rest;
      return { indent, markers, content };
    },

    generateMarker(marker) {
      switch (marker.type) {
        case 'unordered': return '- ';
        case 'ordered': return (marker.value + 1) + '. ';
        case 'task': return '[ ] ';
        default: return '';
      }
    },

    handleEnter(event) {
      const textarea = this.$refs.textarea;
      if (!textarea) return;
      const value = this.markdownText;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;

      if (start !== end) {
        this.insertAtCursor('\n');
        return;
      }

      const lastNewline = value.lastIndexOf('\n', start - 1);
      const lineStart = lastNewline === -1 ? 0 : lastNewline + 1;
      let lineEnd = value.indexOf('\n', start);
      if (lineEnd === -1) lineEnd = value.length;
      const line = value.substring(lineStart, lineEnd);

      if (start !== lineEnd) {
        this.insertAtCursor('\n');
        return;
      }

      const { indent, markers, content } = this.parseLine(line);

      if (markers.length === 0) {
        this.insertAtCursor('\n');
        return;
      }

      if (content.trim() === '') {
        this.removeLine(lineStart, lineEnd);
        return;
      }

      const newMarkerStr = markers.map(m => this.generateMarker(m)).join('');
      const newLine = indent + newMarkerStr;

      const afterText = value.substring(lineEnd);
      const afterHasNewline = afterText.length > 0 && afterText[0] === '\n';
      const afterContent = afterHasNewline ? afterText.substring(1) : afterText;

      const before = value.substring(0, lineStart);
      const currentLineContent = value.substring(lineStart, lineEnd);

      let updatedAfter = afterContent;
      if (markers.some(m => m.type === 'ordered')) {
        const lines = afterContent.split(/(?<=\n)/);
        const newAfterLines = [];
        let stillInSameList = true;
        for (let rawLine of lines) {
          const hasTrailingNewline = rawLine.endsWith('\n');
          const lineStr = hasTrailingNewline ? rawLine.slice(0, -1) : rawLine;

          if (!stillInSameList) {
            newAfterLines.push(rawLine);
            continue;
          }

          if (lineStr === '') {
            stillInSameList = false;
            newAfterLines.push(rawLine);
            continue;
          }

          const parsed = this.parseLine(lineStr);
          const currentMarkerTypes = markers.map(m => m.type);
          const parsedMarkerTypes = parsed.markers.map(m => m.type);
          const sameMarkers = parsed.markers.length === markers.length &&
            currentMarkerTypes.every((type, idx) => type === parsedMarkerTypes[idx]);

          const sameIndent = parsed.indent === indent;

          if (sameMarkers && sameIndent) {
            const updatedMarkers = parsed.markers.map(m => {
              if (m.type === 'ordered') {
                return { type: 'ordered', value: m.value + 1 };
              }
              return { ...m };
            });
            const updatedLine = parsed.indent +
              updatedMarkers.map(m => {
                if (m.type === 'unordered') return '- ';
                if (m.type === 'ordered') return m.value + '. ';
                if (m.type === 'task') return '[ ] ';
              }).join('') + parsed.content;
            newAfterLines.push(updatedLine + (hasTrailingNewline ? '\n' : ''));
          } else {
            stillInSameList = false;
            newAfterLines.push(rawLine);
          }
        }
        updatedAfter = newAfterLines.join('');
      }

      const newText = before + currentLineContent + '\n' + newLine +
        (afterHasNewline ? '\n' : '') + updatedAfter;
      this.markdownText = newText;

      this.$nextTick(() => {
        const textarea = this.$refs.textarea;
        if (textarea) {
          textarea.focus();
          const pos = before.length + currentLineContent.length + 1 + newLine.length;
          textarea.setSelectionRange(pos, pos);
        }
      });
    },

    insertAtCursor(text) {
      const textarea = this.$refs.textarea;
      if (!textarea) return;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const value = this.markdownText;
      const newValue = value.substring(0, start) + text + value.substring(end);
      this.markdownText = newValue;
      this.$nextTick(() => {
        textarea.focus();
        const newPos = start + text.length;
        textarea.setSelectionRange(newPos, newPos);
      });
    },

    removeLine(lineStart, lineEnd) {
      const value = this.markdownText;
      const hasNewline = lineEnd < value.length && value[lineEnd] === '\n';
      let newValue;
      if (hasNewline) {
        newValue = value.substring(0, lineStart) + value.substring(lineEnd + 1);
      } else {
        newValue = value.substring(0, lineStart) + value.substring(lineEnd);
      }
      this.markdownText = newValue;
      this.$nextTick(() => {
        const textarea = this.$refs.textarea;
        if (textarea) {
          textarea.focus();
          const newPos = Math.min(lineStart, newValue.length);
          textarea.setSelectionRange(newPos, newPos);
        }
      });
    },
  },
};
</script>
<style scoped>
/* 移除所有按钮的默认轮廓，统一使用 .focused 类控制焦点 */
.tool-button,
.tabItem,
.dots-button {
  outline: none;
}

.tool-button::after {
  content: attr(data-tooltip);
  position: absolute;
  top: calc(100% + .9rem - 8px);
  left: 50%;
  transform: translateX(-50%);
  background-color: #25292e;
  color: #ffffff;
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: 5px;
  white-space: nowrap;
  z-index: 10;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.dark .tool-button::after {
  background-color: #3d444d;
}

.tool-button:hover::after {
  opacity: 1;
}

.tabItem.focused,
.tool-button.focused {
  box-shadow: 0 0 0 2px #1f6feb;
  outline: none;
  border-color: transparent;
  z-index: 1;
}

.dots-button:focus {
  outline: none;
  border-color: transparent;
}

.dropdown-item.focused {
  box-shadow: 0 0 0 2px #1f6feb;
}

/* 以下为原有样式，完整保留 */
.mdinput {
  display: flex;
  flex-direction: column;
  background: #f6f8fa;
  border: 1px solid #d1d9e0;
  border-radius: 5px;
  margin-top: 1rem;
  transition: border-color 0.2s ease;
}

.dark .mdinput {
  border-color: #3d444d;
}

.mdinput.has-content {
  border-color: #1f6feb;
}

.menu {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f6f8fa;
}

.dark .menu {
  background-color: #151b23;
}

.tabs {
  display: flex;
  gap: 4px;
}

.tabItem {
  padding: 9px 16px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  border-radius: 5px 5px 0 0;
  transition: background 0.1s;
  border: 1px solid transparent;
  border-bottom-color: transparent;
}

.tabItem.active {
  background: #ffffff;
  color: #1f2328;
  border-color: #d1d9e0 #d1d9e0 transparent #d1d9e0;
  border-style: solid;
  border-width: 1px;
}

.tabItem:not(.active) {
  background: #f6f8fa;
  color: #59636e;
}

.tabItem:hover {
  background: rgba(0, 0, 0, 0.05);
}

.dark .tabItem {
  background-color: #151b23;
}

.dark .tabItem.active {
  border-color: #3d444d #3d444d transparent #3d444d;
  color: inherit;
  background-color: #0d1117;
}

.dark .tabItem:not(.active) {
  background-color: #151b23;
  color: #9198a1;
}

.tools {
  display: flex;
  align-items: center;
  position: relative;
}

.tool-button {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  padding: 0;
  color: #59636e;
  position: relative;
  overflow: visible;
}

:deep(.item-svg) {
  width: 16px;
  height: 16px;
  fill: #59636e;
}

:deep(.dark .item-svg) {
  fill: #9198a1;
}

.tool-button:hover {
  background: #eaedf0;
}

.tool-button:active {
  background: #e4e8ec;
}

.dark .tool-button:hover {
  background: #252c34;
}

.dark .tool-button:active {
  color: #292f38;
}

.splitLine {
  border-left: 1px solid #dce2e8;
  padding: 0 8px;
  height: 20px;
  align-self: center;
}

.dark .splitLine {
  border-left-color: #313840;
}

.dots-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 192px;
  background: #ffffff;
  border: 1px solid #e0e4e8;
  border-radius: 16px;
  box-shadow:
    0px 0px 0px 1px #d1d9e080,
    0px 6px 12px -3px #25292e0a,
    0px 6px 18px 0px #25292e1f;
  z-index: 100;
  margin-top: 4px;
  padding: 5px 12px;
  list-style: none;
  max-height: 320px;
  overflow-y: auto;
  transition:
    opacity var(--transition-time) cubic-bezier(0.2, 0.9, 0.3, 1.1),
    transform var(--transition-time) cubic-bezier(0.2, 0.9, 0.3, 1.1);
}

.dark .dots-dropdown {
  background-color: #0d1117;
  border-color: #3d444d;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  margin: 0;
  cursor: pointer;
  color: #1f2328;
  font-size: 0.875rem;
  transition: background 0.15s;
}

.dark .dropdown-item {
  color: #e1f6ed;
}

.dropdown-item:not(.divider):hover {
  background: #f2f3f4;
}

.dropdown-item:not(.divider):active {
  background: #eceff0;
}

.dark .dropdown-item:not(.divider):hover {
  background: #15191f;
}

.dark .dropdown-item:not(.divider):active {
  background: #1a1e25;
}

.dropdown-item.divider {
  padding: 0;
  cursor: default;
  background: transparent;
}

.dropdown-item .item-content {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.dropdown-item .item-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  color: #59636e;
}

.dropdown-item .item-icon svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.dropdown-item .item-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-divider {
  margin: 0;
  border: none;
  border-top: 1px solid #dfe4e9;
  width: 100%;
}

.dark .dropdown-divider {
  border-top-color: #2b3139;
}

.mdTextArea,
.mdPreview {
  background: #ffffff;
  width: 100%;
  border: none;
  resize: vertical;
  min-height: 140px;
  height: calc(100% - 40px);
  color: #1f2328;
  font-family: inherit;
  font-size: 0.875rem;
  padding: 16px;
  border-top: none;
  box-sizing: border-box;
}

.mdPreview {
  overflow-y: auto;
  line-height: 1.5;
}

.mdPreview :deep(h1),
.mdPreview :deep(h2),
.mdPreview :deep(h3),
.mdPreview :deep(h4),
.mdPreview :deep(h5),
.mdPreview :deep(h6) {
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
  line-height: 1.25;
}

.mdPreview :deep(p) {
  margin-top: 0;
  margin-bottom: 0.75em;
}

.mdPreview :deep(ul),
.mdPreview :deep(ol) {
  padding-left: 1.5em;
  margin-bottom: 0.75em;
}

.mdPreview :deep(code) {
  background: rgba(175, 184, 193, 0.2);
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: monospace;
}

.mdPreview :deep(pre) {
  background: #f6f8fa;
  padding: 1em;
  border-radius: 4px;
  overflow-x: auto;
}

.mdPreview :deep(blockquote) {
  margin: 0 0 0.75em 0;
  padding-left: 1em;
  border-left: 4px solid #d1d9e0;
  color: #57606a;
}

.mdPreview :deep(img) {
  max-width: 100%;
  height: auto;
}

.mdPreview :deep(a) {
  color: #1f6feb;
  text-decoration: none;
}

.mdPreview :deep(a:hover) {
  text-decoration: underline;
}

.mdTextArea::placeholder {
  color: #59636e;
}

.dark .mdTextArea,
.dark .mdPreview {
  background-color: #0d1117;
  color: inherit;
}

.dark .mdTextArea::placeholder {
  color: #9198a1;
}

.bottom-addFile {
  padding-top: 8px;
  color: #59636e;
}

.file-Btn {
  padding: 8px;
  border-radius: .375rem;
}

.file-Btn:hover {
  background-color: #f2f3f4
}

.file-Btn span {
  display: flex;
  flex-direction: row;
  gap:5px
}

.dark .bottom-addFile {
  color: #9198a1;
}

.dark .file-Btn:hover {
  background-color: #15191f;
}
</style>