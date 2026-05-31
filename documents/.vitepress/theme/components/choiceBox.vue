<template>
  <div
    class="custom-select"
    :class="{ open: isOpen }"
    ref="selectContainer"
  >
    <div
      class="select-button"
      role="button"
      tabindex="0"
      :aria-expanded="isOpen"
      aria-haspopup="listbox"
      @click="handleButtonClick"
      @keydown.enter.prevent="handleButtonEnter"
      @keydown.space.prevent="handleButtonEnter"
    >
      <span class="selected-text">
        {{ buttonLabel }}
      </span>
      <!-- 显示更多工具 -->
      <span class="svg-icon">
        <svg aria-hidden="true" focusable="false" viewBox="0 0 16 16" width="16" height="16" fill="currentColor" display="inline-block" overflow="visible" style="vertical-align: text-bottom;">
          <path d="m4.427 7.427 3.396 3.396a.25.25 0 0 0 .354 0l3.396-3.396A.25.25 0 0 0 11.396 7H4.604a.25.25 0 0 0-.177.427Z" />
        </svg>
      </span>
    </div>

    <ul
      class="select-dropdown"
      role="listbox"
      :aria-hidden="!isOpen"
      ref="dropdown"
    >
      <li
        v-for="(opt, idx) in options"
        :key="opt.value"
        class="option"
        :class="{
          selected: isSelected(opt),
          focused: focusVisible && focusedIndex === idx
        }"
        role="option"
        :aria-selected="isSelected(opt)"
        @click="selectOption(opt)"
        @mouseenter="onMouseEnterOption"
      >
        <span class="checkmark-placeholder">
          <svg
            v-if="isSelected(opt)"
            aria-hidden="true"
            focusable="false"
            viewBox="0 0 16 16"
            width="16"
            height="16"
            fill="currentColor"
            style="vertical-align: text-bottom;"
          >
            <path d="M13.78 4.22a.75.75 0 0 1 0 1.06l-7.25 7.25a.75.75 0 0 1-1.06 0L2.22 9.28a.751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018L6 10.94l6.72-6.72a.75.75 0 0 1 1.06 0Z" />
          </svg>
        </span>
        {{ opt.label }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'CustomSelect',
  props: {
    modelValue: {
      type: [String, Number, Array],
      default: null
    },
    options: {
      type: Array,
      default: () => []
    },
    placeholder: {
      type: String,
      default: 'None'
    },
    multiple: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      isOpen: false,
      internalValue: this.multiple ? [] : '',
      focusedIndex: 0,
      focusVisible: false,
    };
  },
  computed: {
    actualValue: {
      get() {
        if (this.modelValue !== null && this.modelValue !== undefined) {
          if (this.multiple && !Array.isArray(this.modelValue)) {
            console.warn('[CustomSelect] 多选模式下 modelValue 应为数组，已自动转换');
            return [];
          }
          return this.modelValue;
        }
        return this.internalValue;
      },
      set(newVal) {
        if (this.modelValue !== null && this.modelValue !== undefined) {
          this.$emit('update:modelValue', newVal);
        } else {
          this.internalValue = newVal;
        }
      }
    },
    selectedOptions() {
      if (this.multiple) {
        const values = Array.isArray(this.actualValue) ? this.actualValue : [];
        return this.options.filter(opt => values.includes(opt.value));
      } else {
        const selected = this.options.find(opt => opt.value === this.actualValue);
        return selected ? [selected] : [];
      }
    },
    buttonLabel() {
      if (this.multiple) {
        const count = this.selectedOptions.length;
        if (count === 0) return this.placeholder;
        return this.selectedOptions.map(opt => opt.label).join(', ');
      } else {
        return this.selectedOptions[0]?.label || this.placeholder;
      }
    }
  },
  watch: {
    focusedIndex() {
      if (this.isOpen && this.focusVisible) {
        this.$nextTick(() => {
          this.scrollFocusedIntoView();
        });
      }
    },
    options: {
      handler(newOpts) {
        if (newOpts.length === 0) {
          this.focusedIndex = 0;
        } else if (this.focusedIndex >= newOpts.length) {
          this.focusedIndex = newOpts.length - 1;
        }
      },
      immediate: true
    }
  },
  methods: {
    isSelected(opt) {
      return this.selectedOptions.some(selected => selected.value === opt.value);
    },

    openDropdown(keyboardTriggered = false) {
      if (this.options.length === 0) return;
      this.isOpen = true;
      this.focusedIndex = 0;
      this.focusVisible = keyboardTriggered;
      if (keyboardTriggered) {
        this.$nextTick(() => {
          this.scrollFocusedIntoView();
        });
      }
    },

    closeDropdown() {
      this.isOpen = false;
      this.focusVisible = false;
      this.focusedIndex = 0;
    },

    handleButtonClick() {
      if (this.isOpen) {
        this.closeDropdown();
      } else {
        this.openDropdown(false);
      }
    },

    handleButtonEnter(event) {
      if (this.isOpen) {
        // 下拉已打开：让事件继续传播，由全局监听器处理选择
        // 不阻止冒泡，也不阻止默认（默认已被 .prevent 阻止）
        return;
      } else {
        // 下拉未打开：打开下拉，并阻止事件冒泡，避免全局监听器响应
        event.stopPropagation();
        this.openDropdown(true);
      }
    },

    selectOption(opt) {
      if (this.multiple) {
        let newValues = Array.isArray(this.actualValue) ? [...this.actualValue] : [];
        const valueIndex = newValues.indexOf(opt.value);
        if (valueIndex === -1) {
          newValues.push(opt.value);
        } else {
          newValues.splice(valueIndex, 1);
        }
        this.actualValue = newValues;
      } else {
        if (this.actualValue !== opt.value) {
          this.actualValue = opt.value;
        }
        this.$nextTick(() => {
          this.$refs.selectContainer.querySelector('.select-button').focus();
        });
      }
      this.closeDropdown();
    },

    onMouseEnterOption() {
      // 鼠标移入不影响键盘焦点
    },

    handleDocumentKeyDown(event) {
      if (!this.isOpen) return;

      const key = event.key;
      const count = this.options.length;
      if (count === 0) return;

      // 阻止默认滚动
      if (['ArrowDown', 'ArrowUp', 'Enter', 'Escape', 'Home', 'End'].includes(key)) {
        event.preventDefault();
      }

      if (key === 'Escape') {
        this.closeDropdown();
        this.$refs.selectContainer.querySelector('.select-button').focus();
        return;
      }

      if (key === 'ArrowDown' || key === 'ArrowUp') {
        if (!this.focusVisible) {
          this.focusVisible = true;
          if (key === 'ArrowDown') {
            this.focusedIndex = Math.min(1, count - 1);
          } else {
            this.focusedIndex = count - 1;
          }
        } else {
          if (key === 'ArrowDown') {
            this.focusedIndex = (this.focusedIndex + 1) % count;
          } else {
            this.focusedIndex = (this.focusedIndex - 1 + count) % count;
          }
        }
        return;
      }

      if (key === 'Enter') {
        if (this.focusVisible) {
          const opt = this.options[this.focusedIndex];
          if (opt) this.selectOption(opt);
        } else {
          // 默认选择第一个选项
          if (this.options.length > 0) {
            this.selectOption(this.options[0]);
          }
        }
        return;
      }

      if (key === 'Home') {
        this.focusVisible = true;
        this.focusedIndex = 0;
      } else if (key === 'End') {
        this.focusVisible = true;
        this.focusedIndex = count - 1;
      }
    },

    scrollFocusedIntoView() {
      if (!this.isOpen || !this.focusVisible) return;
      const dropdown = this.$refs.dropdown;
      if (!dropdown) return;
      const optionElements = dropdown.querySelectorAll('.option');
      const target = optionElements[this.focusedIndex];
      if (target) {
        target.scrollIntoView({ block: 'nearest', behavior: 'auto' });
      }
    },

    handleClickOutside(event) {
      if (this.$refs.selectContainer && !this.$refs.selectContainer.contains(event.target)) {
        this.closeDropdown();
      }
    }
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
    document.addEventListener('keydown', this.handleDocumentKeyDown);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
    document.removeEventListener('keydown', this.handleDocumentKeyDown);
  }
};
</script>

<style scoped>
.custom-select {
  position: relative;
  display: inline-block;
  font-size: 14px;
  --radius: 5px;
  --dropdown-radius: 16px;
  --option-radius: 5px;
  --transition-time: 0.22s;
  --focus-color: #1f6feb;
  --press-bg: #eff2f5;
}

.select-button {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: auto;
  max-width: 365px;
  padding: 0 12px;
  background: #f6f8fa;
  border: 1px solid #d1d9e0;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 500;
  color: inherit;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  line-height: 1.4;
  gap: 15px;
  white-space: nowrap;
  user-select: none;
}

.dark .select-button {
  background: #212830;
  border-color: #3d444d;
}

.select-button:hover {
  background: #eff2f5;
}

.dark .select-button:hover {
  background: #262c36;
}

.select-button:focus {
  outline: none;
  box-shadow: 0 0 0 2px var(--focus-color);
  border-color: transparent;
}

.selected-text {
  flex: 1;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  height: 100%;
  font-family: -apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji";
  font-size: 14px;
  line-height: 30px;
}

.svg-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: #5f6c80;
  transition: none;
}

.svg-icon svg {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.dark .svg-icon svg {
  fill: #9198a1;
}

.select-dropdown {
  position: absolute;
  bottom: calc(100% + 10px);
  left: 0;
  width: 100%;
  min-width: 320px;
  max-width: 320px;
  max-height: 320px;
  overflow-y: auto;
  background: white;
  border-radius: var(--dropdown-radius);
  box-shadow: 0px 0px 0px 1px #d1d9e080, 0px 6px 12px -3px #25292e0a, 0px 6px 18px 0px #25292e1f;
  z-index: 50;
  opacity: 0;
  transform: translateY(10px);
  pointer-events: none;
  transition: opacity var(--transition-time) cubic-bezier(0.2, 0.9, 0.3, 1.1),
              transform var(--transition-time) cubic-bezier(0.2, 0.9, 0.3, 1.1);
  padding: 8px 8px;
  margin: 0;
  list-style: none;
}

.dark .select-dropdown {
  background: #010409;
  color: inherit;
}

.custom-select.open .select-dropdown {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.option {
  display: flex;
  align-items: flex-start;
  padding: 6px 8px;
  font-size: 14px;
  color: #1e293b;
  cursor: pointer;
  background: white;
  border-radius: var(--option-radius);
  transition: background 0.15s, color 0.15s, box-shadow 0.15s;
  white-space: normal;
  word-break: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
  margin: 0 8px;
  box-sizing: border-box;
  position: relative;
  z-index: 0;
  user-select: none;
}

.dark .option {
  background: #010409;
  color: inherit;
}

.option.focused {
  box-shadow: 0 0 0 2px var(--focus-color);
  z-index: 1;
}

.option:active {
  background-color: var(--press-bg);
}

.dark .option:active {
  background-color: #1a1e25; /* 暗色按下背景 */
}

.checkmark-placeholder {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  margin-right: 8px;
  flex-shrink: 0;
}

.checkmark-placeholder svg {
  width: 100%;
  height: 100%;
  fill: currentColor;
}

.dark .checkmark-placeholder svg {
  fill: #9198a1;
}

.option:hover {
  background: #f2f3f4;
}

.dark .option:hover {
  background: #15191f;
}
</style>