<template>
    <div class="strong">
        <slot />
        <div class="roundCardRow">
            <!-- Assignee 按钮 -->
            <div
                ref="assigneeButtonRef"
                class="roundCard notActive"
                @click.stop="toggleMenu"
            >
                <svg
                    class="svg"
                    viewBox="0 0 16 16"
                    width="16"
                    height="16"
                    fill="currentColor"
                >
                    <path
                        d="M2 5.5a3.5 3.5 0 1 1 5.898 2.549 5.508 5.508 0 0 1 3.034 4.084.75.75 0 1 1-1.482.235 4 4 0 0 0-7.9 0 .75.75 0 0 1-1.482-.236A5.507 5.507 0 0 1 3.102 8.05 3.493 3.493 0 0 1 2 5.5ZM11 4a3.001 3.001 0 0 1 2.22 5.018 5.01 5.01 0 0 1 2.56 3.012.749.749 0 0 1-.885.954.752.752 0 0 1-.549-.514 3.507 3.507 0 0 0-2.522-2.372.75.75 0 0 1-.574-.73v-.352a.75.75 0 0 1 .416-.672A1.5 1.5 0 0 0 11 5.5.75.75 0 0 1 11 4Zm-5.5-.5a2 2 0 1 0-.001 3.999A2 2 0 0 0 5.5 3.5Z"
                    ></path>
                </svg>
                {{ LangPack.Assignee ?? 'Assignee' }}
            </div>
            <div class="roundCard">
                {{ LangPack.LabelDesc ?? 'Label' }}
                <svg
                    viewBox="0 0 16 16"
                    width="16"
                    height="16"
                    :fill="LabelColor"
                >
                    <circle cx="8" cy="8" r="5"></circle>
                </svg>
                <b>{{ LangPack.Label ?? 'None' }}</b>
            </div>
            <div class="roundCard">
                {{ LangPack.TypeDesc ?? 'Label' }}
                <svg
                    class="svg"
                    viewBox="0 0 16 16"
                    width="16"
                    height="16"
                    :fill="TypeColor"
                >
                    <circle cx="8" cy="8" r="5"></circle>
                </svg>
                <b>{{ LangPack.Type ?? 'None' }}</b>
            </div>
            <div class="roundCard notActive">
                <svg
                    class="svg"
                    viewBox="0 0 16 16"
                    width="16"
                    height="16"
                    fill="currentColor"
                >
                    <path d="m5.06 7.356 2.795 2.833c.08.081.21.081.29 0l2.794-2.833c.13-.131.038-.356-.145-.356H5.206c-.183 0-.275.225-.145.356Z"></path>
                    <path d="M1 2.75C1 1.784 1.784 1 2.75 1h10.5c.966 0 1.75.784 1.75 1.75v10.5A1.75 1.75 0 0 1 13.25 15H2.75A1.75 1.75 0 0 1 1 13.25Zm1.75-.25a.25.25 0 0 0-.25.25v10.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25V2.75a.25.25 0 0 0-.25-.25Z"></path>
                </svg>
                {{ LangPack.Priority ?? 'Priority' }}
            </div>
            <div class="roundCard notActive" v-if="ShowDate">
                <svg
                    class="svg"
                    viewBox="0 0 16 16"
                    width="16"
                    height="16"
                    fill="currentColor"
                >
                    <path d="M4.75 0a.75.75 0 0 1 .75.75V2h5V.75a.75.75 0 0 1 1.5 0V2h1.25c.966 0 1.75.784 1.75 1.75v10.5A1.75 1.75 0 0 1 13.25 16H2.75A1.75 1.75 0 0 1 1 14.25V3.75C1 2.784 1.784 2 2.75 2H4V.75A.75.75 0 0 1 4.75 0ZM2.5 7.5v6.75c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25V7.5Zm10.75-4H2.75a.25.25 0 0 0-.25.25V6h11V3.75a.25.25 0 0 0-.25-.25Z"></path>
                </svg>
                {{ LangPack.StartDate ?? 'Start date' }}
            </div>
            <div class="roundCard notActive" v-if="ShowDate">
                <svg
                    class="svg"
                    viewBox="0 0 16 16"
                    width="16"
                    height="16"
                    fill="currentColor"
                >
                    <path d="M4.75 0a.75.75 0 0 1 .75.75V2h5V.75a.75.75 0 0 1 1.5 0V2h1.25c.966 0 1.75.784 1.75 1.75v10.5A1.75 1.75 0 0 1 13.25 16H2.75A1.75 1.75 0 0 1 1 14.25V3.75C1 2.784 1.784 2 2.75 2H4V.75A.75.75 0 0 1 4.75 0ZM2.5 7.5v6.75c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25V7.5Zm10.75-4H2.75a.25.25 0 0 0-.25.25V6h11V3.75a.25.25 0 0 0-.25-.25Z"></path>
                </svg>
                {{ LangPack.TargetDate ?? 'Target date' }}
            </div>
            <div class="roundCard notActive">
                <svg
                    class="svg"
                    viewBox="0 0 16 16"
                    width="16"
                    height="16"
                    fill="currentColor"
                >
                    <path d="m5.06 7.356 2.795 2.833c.08.081.21.081.29 0l2.794-2.833c.13-.131.038-.356-.145-.356H5.206c-.183 0-.275.225-.145.356Z"></path>
                    <path d="M1 2.75C1 1.784 1.784 1 2.75 1h10.5c.966 0 1.75.784 1.75 1.75v10.5A1.75 1.75 0 0 1 13.25 15H2.75A1.75 1.75 0 0 1 1 13.25Zm1.75-.25a.25.25 0 0 0-.25.25v10.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25V2.75a.25.25 0 0 0-.25-.25Z"></path>
                </svg>
                {{ LangPack.Effort ?? 'Effort' }}
            </div>
            <div class="divider"></div>
            <div class="roundCard notActive">
                <svg
                    class="svg"
                    viewBox="0 0 16 16"
                    width="16"
                    height="16"
                    fill="currentColor"
                >
                    <path
                        d="M0 1.75C0 .784.784 0 1.75 0h12.5C15.216 0 16 .784 16 1.75v12.5A1.75 1.75 0 0 1 14.25 16H1.75A1.75 1.75 0 0 1 0 14.25ZM6.5 6.5v8h7.75a.25.25 0 0 0 .25-.25V6.5Zm8-1.5V1.75a.25.25 0 0 0-.25-.25H6.5V5Zm-13 1.5v7.75c0 .138.112.25.25.25H5v-8ZM5 5V1.5H1.75a.25.25 0 0 0-.25.25V5Z"
                    ></path>
                </svg>
                {{ LangPack.Project ?? 'Project' }}
            </div>
            <div class="roundCard notActive">
                <svg
                    class="svg"
                    viewBox="0 0 16 16"
                    width="16"
                    height="16"
                    fill="currentColor"
                >
                    <path
                        d="M7.75 0a.75.75 0 0 1 .75.75V3h3.634c.414 0 .814.147 1.13.414l2.07 1.75a1.75 1.75 0 0 1 0 2.672l-2.07 1.75a1.75 1.75 0 0 1-1.13.414H8.5v5.25a.75.75 0 0 1-1.5 0V10H2.75A1.75 1.75 0 0 1 1 8.25v-3.5C1 3.784 1.784 3 2.75 3H7V.75A.75.75 0 0 1 7.75 0Zm4.384 8.5a.25.25 0 0 0 .161-.06l2.07-1.75a.248.248 0 0 0 0-.38l-2.07-1.75a.25.25 0 0 0-.161-.06H2.75a.25.25 0 0 0-.25.25v3.5c0 .138.112.25.25.25h9.384Z"
                    ></path>
                </svg>
                {{ LangPack.Milestone ?? 'Milestone' }}
            </div>
        </div>
        <div class="footer-tip">
            <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor">
                <path
                    d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8Zm8-6.5a6.5 6.5 0 1 0 0 13 6.5 6.5 0 0 0 0-13ZM6.5 7.75A.75.75 0 0 1 7.25 7h1a.75.75 0 0 1 .75.75v2.75h.25a.75.75 0 0 1 0 1.5h-2a.75.75 0 0 1 0-1.5h.25v-2h-.25a.75.75 0 0 1-.75-.75ZM8 6a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z"
                ></path>
            </svg>
            <span>
                {{
                    LangPack.Product ??
                    'Remember, contributions to this repository should follow its'
                }}
                <a
                    href="https://github.com/xystudiocode/pyClickMouse/blob/main/CONTRIBUTING.md"
                    >{{ LangPack.GuideLines ?? 'contributing guidelines' }}</a
                >
                {{ LangPack.And ?? 'and' }}
                <a
                    href="https://github.com/xystudiocode/pyClickMouse/security/policy"
                    >{{ LangPack.Security ?? 'security policy' }}</a
                >.</span
            >
        </div>
        <footer class="button-footer">
            <div class="checkbox-line">
                <input type="checkbox" class="checkbox" />
                {{ LangPack.CreateMore ?? 'Create more' }}
            </div>
            <div class="buttons">
                <div class="button">
                    <span class="text">{{ LangPack.Cancel ?? 'Cancel' }}</span>
                </div>
                <div
                    class="button button-highlight"
                    :class="{ hovered: isHovered }"
                    @mouseenter="isHovered = true"
                    @mouseleave="isHovered = false"
                >
                    <span class="text text-highlight">{{
                        LangPack.Create ?? 'Create'
                    }}</span>
                    <span class="fastkey" :class="{ hovered: isHovered }">
                        ^⏎
                    </span>
                </div>
            </div>
        </footer>
    </div>

    <!-- 弹出菜单：左边缘与 Assignee 按钮左边缘对齐，位于按钮上方 35x -->
    <!-- <transition name="menu-pop">
        <div
            v-if="showMenu"
            ref="menuRef"
            class="strong buttonMenu assigneePopup"
            :style="menuStyle"
            @click.stop
        >
            <div class="MenuTitle">
                <p class="bold">{{ LangPack.assigneeSelect ?? 'Select Assignees' }}</p>
                <div class="searchBox">
                    <svg aria-hidden="true" focusable="false" viewBox="0 0 16 16" width="16" height="16" fill="currentColor" display="inline-block" overflow="visible" style="vertical-align: text-bottom;">
                        <path d="M10.68 11.74a6 6 0 0 1-7.922-8.982 6 6 0 0 1 8.982 7.922l3.04 3.04a.749.749 0 0 1-.326 1.275.749.749 0 0 1-.734-.215ZM11.5 7a4.499 4.499 0 1 0-8.997 0A4.499 4.499 0 0 0 11.5 7Z"></path>
                    </svg>
                    <input
                        type="text"
                        :placeholder="LangPack.filterAssignees ?? 'Filter assignees'"
                        class="filter-input"
                        @click.stop
                    />
                </div>
            </div>
            <div class="MenuContent">
                <div class="assigneeList">
                    <p class="smallTitle">{{ LangPack.assigneeNotFound ?? 'No assignees were found' }}</p>
                    <p class="desc">{{ LangPack.assigneeNotFoundDesc ?? 'Try searching for a different name for results.' }}</p>
                </div>
            </div>
        </div>
    </transition> -->
    <!-- 没有完成，先禁用了 -->
</template>

<script setup>
import { ref, nextTick, onBeforeUnmount } from 'vue';

defineOptions({
    name: 'strongCard',
});

defineProps({
    LabelColor: {
        type: String,
    },
    TypeColor: {
        type: String,
    },
    LabelText: {
        type: String,
    },
    LangPack: {
        type: Object,
        default: () => ({}),
    },
    ShowDate: {
        type: Boolean,
        default: false,
    },
});

const showMenu = ref(false);
const menuRef = ref(null);
const assigneeButtonRef = ref(null);
const menuStyle = ref({
    position: 'fixed',
    left: 'auto',
    top: 'auto',
    visibility: 'visible',
});
const isHovered = ref(false);

function closeMenu() {
    showMenu.value = false;
    document.removeEventListener('click', handleDocumentClick);
    window.removeEventListener('resize', closeMenu);
}

function handleDocumentClick(event) {
    const menuEl = menuRef.value;
    const buttonEl = assigneeButtonRef.value;
    if (menuEl && menuEl.contains(event.target)) return;
    if (buttonEl && buttonEl.contains(event.target)) return;
    closeMenu();
}

async function toggleMenu() {
    if (showMenu.value) {
        closeMenu();
        return;
    }

    const button = assigneeButtonRef.value;
    if (!button) return;

    const buttonRect = button.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const menuWidth = 320; // 固定宽度

    // 左边缘对齐按钮左边缘
    let left = buttonRect.left;
    // 避免超出右边界（若超出则右对齐，但仍优先左对齐原则，简单处理）
    if (left + menuWidth > viewportWidth) {
        left = viewportWidth - menuWidth - 8;
    }
    if (left < 8) left = 8;

    menuStyle.value.left = `${left}px`;
    showMenu.value = true;

    await nextTick();
    const menuEl = menuRef.value;
    if (menuEl) {
        const menuHeight = menuEl.offsetHeight;
        let top = buttonRect.top - menuHeight - 5;
        if (top < 8) top = 8;
        menuStyle.value.top = `${top}px`;
    } else {
        menuStyle.value.top = `${buttonRect.top - 360 - 5}px`;
    }

    document.addEventListener('click', handleDocumentClick);
    window.addEventListener('resize', closeMenu, { once: true });
}

onBeforeUnmount(() => {
    document.removeEventListener('click', handleDocumentClick);
    window.removeEventListener('resize', closeMenu);
});
</script>

<style scoped>
/* 弹出菜单固定定位基础样式 */
.assigneePopup {
    position: fixed;
    z-index: 1000;
    width: 320px;
    margin: 0;
    box-shadow: 0 0 0 1px #d1d9e040, 0 6px 12px -3px #25292e0a, 0 6px 18px 0 #25292e1f;
}

/* 从下往上渐显动画，无回弹 */
.menu-pop-enter-active,
.menu-pop-leave-active {
    transition: opacity 0.1s ease-out, transform 0.1s ease-out;
}

.menu-pop-enter-from,
.menu-pop-leave-to {
    opacity: 0;
    transform: translateY(8px);
}

.menu-pop-enter-to,
.menu-pop-leave-from {
    opacity: 1;
    transform: translateY(0);
}

/* 搜索框聚焦样式 */
.searchBox {
    display: flex;
    align-items: center;
    border: 1px solid #d1d9e0;
    border-radius: .375rem;
    margin: 8px;
    padding-left: 8px;
    width: calc(100% - 16px);
    height: 30px;
    background-color: #ffffff;
    transition: border 0.1s ease;
}

.dark .searchBox {
    border-color: #3d444d;
    background-color: #0d1117;
}

.searchBox:focus-within {
    border: 2px solid #1f6feb;
    margin: 7px;
    width: calc(100% - 14px);
    padding-left: 7px;
}

.searchBox svg {
    fill: #59636e;
    margin-right: 6px;
    flex-shrink: 0;
}

.dark .searchBox svg {
    fill: #9198a1;
}

.filter-input {
    flex: 1;
    border: none;
    outline: none;
    background: transparent;
    font-size: 0.875rem;
    padding: 6px 0;
    color: #1f2328;
    font-family: inherit;
}

.dark .filter-input {
    color: #f0f6fc;
}

.filter-input::placeholder {
    color: #6e7781;
    user-select: none;
}

.dark .filter-input::placeholder {
    color: #8d96a0;
}

/* 以下为原样式（保持原有卡片、按钮等外观） */
.strong {
    background-color: white;
    box-shadow: 0 8px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23);
    border-radius: 5px;
    margin: 10px 0;
    padding-left: 5px;
    word-wrap: break-word;
    line-height: 1.5;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji';
    font-size: 12px;
    box-sizing: border-box;
    padding: 15px 10px;
    color: #1f2328;
}

.divider {
    width: 1px;
    padding: 10px 0;
    border-left: 1px solid #d1d9e0;
}

.dark .divider {
    border-left-color: #3d444d;
}

.roundCardRow {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    user-select: none;
    margin-top: 1.5rem;
}

.roundCard {
    display: flex;
    align-items: center;
    border-radius: 0.375rem;
    border: 0.8px solid #d1d9e0;
    padding: 5px 8px;
    width: auto;
    gap: 0.25rem;
    color: #59636e;
    background-color: #f6f8fa;
    cursor: pointer;
}

.notActive {
    gap: 0;
    border-style: dashed;
}

.dark .roundCard {
    border-color: #3d444d;
}

.notActive .svg {
    margin-right: 4px;
}

.roundCard:hover {
    background-color: #eff2f5;
}

.roundCard:active {
    background-color: #e6eaef;
}

.dark .roundCard {
    background-color: #212830;
    color: #9198a1;
}

.dark .roundCard:hover {
    background-color: #262c36;
}

.dark .roundCard:active {
    background-color: #2a313c;
}

.notActive .svg {
    fill: #59636e;
}

.dark .notActive .svg {
    fill: #9198a1;
}

.roundCard b {
    font-weight: 600;
    color: #25292e;
}

.dark .roundCard b {
    color: white;
}

.dark .strong {
    background-color: #0d1117;
    color: #f0f6fc;
}

.footer-tip {
    display: flex;
    gap: 0.25rem;
    padding-top: 8px;
    color: #9198a1;
}

.footer-tip svg {
    fill: #59636e;
}

.dark .footer-tip svg {
    fill: #9198a1;
}

.button-footer {
    display: flex;
    justify-content: end;
    margin-top: 24px;
    gap: 10px;
}

.button-footer .checkbox-line {
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.button-footer .checkbox {
    height: 1rem;
    width: 1rem;
    border-radius: 5px;
}

.buttons {
    display: flex;
    gap: 10px;
}

.button {
    background-color: #f6f8fa;
    color: #25292e;
    border: 1px solid #d1d9e0;
    border-radius: 6px;
    padding: 0px 12px;
    font-size: 14px;
    font-weight: 500;
    line-height: 2;
    user-select: none;
    cursor: pointer;
}

.text-highlight {
    margin-right: 8px;
}

.fastkey {
    background-color: #1d732e;
    font-weight: 400;
    font-size: 0.75rem;
    border-radius: 4px;
    padding: 2px 2px;
}

.dark .button {
    background-color: #212830;
    border-color: #3d444d;
    color: #f0f6fc;
}

.dark .button:hover {
    background-color: #262c36;
}

.button:hover {
    background-color: #eff2f5;
}

.dark .button:active {
    background-color: #2a313c;
}

.button:active {
    background-color: #e6eaef;
}

.button-highlight,
.dark .button-highlight {
    border-color: #449854;
    background-color: #238636;
    color: #f0f6fc;
}

.button-highlight:hover,
.dark .button-highlight:hover {
    background-color: #29903b;
}
.button-highlight:active,
.dark .button-highlight:active {
    background-color: #2e9a40;
}

.button-highlight:hover .fastkey {
    background-color: #227b32;
}

.button-highlight:active .fastkey {
    background-color: #268336;
}

.buttonMenu {
    font-size: 14px;
    width: 320px;
    margin: 0;
    padding: 0;
    border: 1px solid #d1d9e0;
    border-radius: .75rem;
    font-family: "Mona Sans VF", -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    background-color: white;
}

.dark .buttonMenu {
    border-color: #3d444d;
    background-color: #0d1117;
}

.MenuTitle {
    padding-top: 8px;
    padding-left: 8px;
    padding-right: 8px;
}

.MenuTitle .bold {
    margin-top: 8px;
    margin-left: 8px;
    margin-bottom: 0;
    margin-right: 0;
    font-size: .875rem;
    font-weight: 600;
}

.MenuContent {
    height: 331px;
    width: 100%;
    padding: 8px 0;
    border-top: 1px solid #d1d9e0;
}

.dark .MenuContent {
    border-color: #3d444d;
}

.assigneeList {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.assigneeList p {
    margin: 0;
    padding: 0;
}

.assigneeList .smallTitle {
    font-size: .875rem;
    font-weight: 600;
}

.assigneeList .desc {
    color: #59636e;
    font-size: .75rem;
}

.dark .assigneeList .desc {
    color: #9198a1;
}
</style>