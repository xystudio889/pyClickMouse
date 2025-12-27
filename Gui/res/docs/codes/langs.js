const browserLanguage = navigator.language || navigator.userLanguage;

async function loadJson(file) {
    // 从外部JSON文件加载语言列表

    try {
        const response = await fetch(file);
        if (!response.ok) {
            throw new Error('无法加载JSON文件');
        }
        return await response.json();
    } catch (error) {
        console.error('加载JSON时出错:', error);
        return null;
    }
}

function getSystemLangID(langs) {
    for (const lang in langs) { // 遍历语言列表
        if (langs[lang]['lang_system_name'] === browserLanguage) {
            return lang; // 找到匹配的语言ID并返回
        };
    }
    return 0;
}

function setOption(select, index) {
    select.selectedIndex = index;
}

function getLang(source, index, id) {
    lang = source[index]['lang_package'][id];
    
    if (lang === undefined) {
        lang = source[0]['lang_package'][id];
        if (lang === undefined) {
            console.error('语言包不存在:'+ id);
            return 'Language not found';
        }
    }
    return lang
}

function setText(elementId, text) {
    try {
        const resultElement = document.getElementById(elementId);
        resultElement.innerHTML = text
    } catch (error) {}
}
// 更新显示结果
function updateResult(key, jsonData) {
    document.documentElement.lang = jsonData[key]['lang_system_name'];
    if (document.documentElement.lang === 'en') {
        document.documentElement.lang = 'en-US';
    }

    const metaTags = document.getElementsByTagName('meta');
    for (let i = 0; i < metaTags.length; i++) {
        if (metaTags[i].getAttribute('name') === 'webLang_id') {
            document.title = getLang(jsonData, key, metaTags[i].getAttribute('content'));
        }
    }

    setText('lang_text', getLang(jsonData, key, '01'))
    setText('homeSearch', '<i class="fas fa-search"></i> ' + getLang(jsonData, key, '02'))

    try {
        document.getElementById('searchInput').placeholder = getLang(jsonData, key, '03')
    } catch (error) {}

    setText('searchTitle', getLang(jsonData, key, '04'))
    setText('backToHome', '<i class="fas fa-times"></i> ' + getLang(jsonData, key, '05'))
    setText('resultsCount', getLang(jsonData, key, '07') + '0' + getLang(jsonData, key, '08'))
    setText('clearResults', '<i class="fas fa-times"></i>' +getLang(jsonData, key, '0f'))
    setText('searchHistory', '<i class="fas fa-history"></i>' + getLang(jsonData, key, '10'))
    setText('clearHistory', '<i class="fas fa-trash-alt"></i>' + getLang(jsonData, key, '11'))
}

// 保存选择到本地存储
function saveSelection(key) {
    localStorage.setItem('lang', key);
}

async function main() {
    const langs = await loadJson('./res/langs.json');
    const system_lang = getSystemLangID(langs);
    const select = document.getElementById('langSelector');
    const select_lang = localStorage.getItem('lang'); // 从localStorage获取语言ID
    updateResult(select_lang, langs);
    
    select.addEventListener('change', function() {
        const selectedKey = select.value;
        if (selectedKey) {
            updateResult(selectedKey, langs);
            saveSelection(selectedKey);
        }
    });
    
    if (select_lang === null) { // 不存在名为'lang'的localStorage
        localStorage.setItem('lang', system_lang); // 保存系统语言ID到localStorage
        select_lang = system_lang; // 重新获取语言ID
    }

    setOption(select, select_lang); // 设置下拉列表默认值

}

main();
