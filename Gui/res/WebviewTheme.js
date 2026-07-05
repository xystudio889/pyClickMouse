// -- 1. 覆盖 matchMedia，使 prefers-color-scheme: dark 返回 true --
(function() {
    const _origMatchMedia = window.matchMedia.bind(window);
    window.matchMedia = function(query) {
        const mql = _origMatchMedia(query);
        const regex = new RegExp(`prefers-color-scheme\\s*:\\s*${theme}`, 'i');
        if (regex.test(query)) {
            Object.defineProperty(mql, 'matches', {
                get: () => true,
                configurable: true,
                enumerable: true
            });
        }
        return mql;
    };
})();

// -- 2. 注入 color-scheme，让滚动条、表单控件等原生元素使用深色 --
(function() {
    function injectColorScheme() {
        const style = document.createElement('style');
        style.id = `__qt_${theme}_color_scheme__`;
        style.textContent = `:root { color-scheme: ${theme} !important; }`;
        (document.head || document.documentElement).appendChild(style);
    }
    if (document.head) {
        injectColorScheme();
    } else {
        document.addEventListener('DOMContentLoaded', injectColorScheme);
    }
})();