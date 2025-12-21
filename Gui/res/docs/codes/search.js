// 本地存储搜索历史
let searchDatabase = []

const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const resultsSection = document.getElementById('resultsSection');
const resultsContainer = document.getElementById('resultsContainer');
const resultsCount = document.getElementById('resultsCount');
const historyList = document.getElementById('historyList');
const clearHistoryBtn = document.getElementById('clearHistory');
const clearResultsBtn = document.getElementById('clearResults');

// 初始化搜索历史
let searchHistory = JSON.parse(localStorage.getItem('searchHistory')) || [];

async function loadSearchDatabase() {
    const response = await fetch('./res/searchIndex.json');
    const langs = await loadJson('./res/langs.json');
    const system_lang = getSystemLangID(langs);
    const select_lang = localStorage.getItem('lang')

    if (select_lang === null) {
        localStorage.setItem('lang', system_lang)
        select_lang = system_lang
    }

    searchDatabase = await response.json();

    for (let index in searchDatabase) {
        for (let info in searchDatabase[index]) {
            if (Array.isArray(searchDatabase[index][info])) {
                searchDatabase[index][info] = searchDatabase[index][info][select_lang];
            }
        }
    }
}

// 初始化页面
async function initPage() {
    const langs = await loadJson('./res/langs.json')
    const select_lang = localStorage.getItem('lang')

    // 加载搜索数据库
    await loadSearchDatabase();

    // 渲染搜索历史
    renderSearchHistory();

    // 添加事件监听器
    addEventListeners();

    resultsSection.classList.add('active');
    resultsContainer.innerHTML = `
        <div class="no-results">
            <i class="fas fa-search"></i>
            <h3>${getLang(langs, select_lang, '09')}</h3>
            <p>${getLang(langs, select_lang, '0a')}</p>
        </div>
    `;
    
    // 监听输入框变化，实现实时搜索
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        if (query.length > 0) {
            search(query);
        } else {
            resultsContainer.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h3>${getLang(langs, select_lang, '09')}</h3>
                <p>${getLang(langs, select_lang, '0a')}</p>
            </div>
        `;
        resultsCount.textContent = `${getLang(langs, select_lang, '07')}0 ${getLang(langs, select_lang, '08')}`;
        }
    });
}

// 渲染搜索历史
async function renderSearchHistory() {
    historyList.innerHTML = '';
    const langs = await loadJson('./res/langs.json')
    const select_lang = localStorage.getItem('lang')

    if (searchHistory.length === 0) {
        const emptyItem = document.createElement('li');
        emptyItem.className = 'history-item';
        emptyItem.innerHTML = `<span style="color:#95a5a6;">${getLang(langs, select_lang, '0b')}</span>`;
        historyList.appendChild(emptyItem);
        return;
    }
    
    // 只显示最近的8条记录
    const recentHistory = searchHistory.slice(-8).reverse();
    
    recentHistory.forEach(item => {
        const historyItem = document.createElement('li');
        historyItem.className = 'history-item';
        
        historyItem.innerHTML = `
            <span class="history-query">${item.query}</span>
            <div style="display: flex; align-items: center; gap: 15px;">
                <button class="delete-history" data-query="${item.query}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // 点击搜索历史项
        historyItem.querySelector('.history-query').addEventListener('click', () => {
            searchInput.value = item.query;
            search(item.query);
        });
        
        // 点击删除单个历史记录
        historyItem.querySelector('.delete-history').addEventListener('click', (e) => {
            e.stopPropagation();
            removeFromHistory(item.query);
        });
        
        historyList.appendChild(historyItem);
    });
}

// 执行关键词匹配搜索
async function search(query) {
    const langs = await loadJson('./res/langs.json')
    const select_lang = localStorage.getItem('lang')
    var text_plural = false

    if (!query.trim()) {
        // 搜索为空时
        resultsSection.classList.remove('active');
        return;
    }
    
    // 保存搜索历史
    addToHistory(query);
    
    // 显示结果区域
    resultsSection.classList.add('active');
    
    // 清空之前的搜索结果
    resultsContainer.innerHTML = '';
    
    // 执行搜索
    const searchResults = searchDatabase.filter(item => {
        return matchesSearchCriteria(item, query);
    });
    
    if (langs[select_lang]['has_plural']){
        if (searchResults.length === 1) {
            text_plural = true
        } else {
            text_plural = false
        }
    } else {
        text_plural = false
    }
    // 显示结果数量
    resultsCount.textContent = `${getLang(langs, select_lang, '07')} ${searchResults.length} ${text_plural ? getLang(langs, select_lang, '08').slice(0, -2) : getLang(langs, select_lang, '08')}`;
    
    // 如果没有结果，显示提示信息
    if (searchResults.length === 0) {
        const noResults = document.createElement('div');
        noResults.className = 'no-results';
        noResults.innerHTML = `
            <i class="fas fa-search-minus"></i>
            <h3>${getLang(langs, select_lang, '0c')}</h3>
            <p>${getLang(langs, select_lang, '0d')}</p>
        `;
        resultsContainer.appendChild(noResults);
        return;
    }
    
    // 创建结果列表
    const resultsList = document.createElement('ul');
    resultsList.className = 'results-list';
    
    // 渲染搜索结果
    searchResults.forEach(item => {
        const resultItem = createResultItem(item, query);
        resultsList.appendChild(resultItem);
    });
    
    resultsContainer.appendChild(resultsList);
    
    // 滚动到结果区域
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 判断是否匹配搜索条件
function matchesSearchCriteria(item, query) {
    const searchText = false ? query : query.toLowerCase();
    // 搜索所有字段：标题、内容、分类、标签
    return (
        matchesField(item.title, searchText) ||
        matchesField(item.content, searchText) ||
        matchesField(item.category, searchText) ||
        item.tags.some(tag => matchesField(tag, searchText))
    );
}

// 判断字段是否匹配
function matchesField(fieldValue, searchText) {
    let fieldText = fieldValue;

    fieldText = fieldText.toLowerCase();
    return fieldText.includes(searchText);
}

// 创建搜索结果项
function createResultItem(item, query) {
    const resultItem = document.createElement('li');
    resultItem.className = 'result-item';
    
    const highlightedTitle = highlightMatches(item.title, query);
    const highlightedContent = highlightMatches(item.content.substring(0, 150) + '...', query, true, false);
    
    // 创建标签HTML
    const tagsHtml = item.tags.map(tag => 
        `<span class="result-tag">${tag}</span>`
    ).join('');

    resultItem.innerHTML = `
        <div class="result-title">
            <i class="fas fa-file-alt"></i>
            <a href="${item.url}" target="_blank" class="link">${highlightedTitle}</a>
        </div>
        <div class="result-snippet">
            ${highlightedContent}
        </div>
        <div style="margin-top: 10px; display: flex; gap: 10px; font-size: 14px;">
            <span style="color: #3498db; background-color: #f1f8ff; padding: 3px 8px; border-radius: 12px;">
                ${item.category}
            </span>
            ${tagsHtml}
        </div>
    `;
    
    return resultItem;
}

function highlightMatches(text, query) {
    if (!query.trim()) return text;
    
    const searchWords = query.split(' ').filter(word => word.length > 0);
    let result = text;
    
    // 创建正则表达式模式
    const patterns = searchWords.map(word => {
        // 直接查找包含该词的部分
        return false ? word : new RegExp(word, 'gi');
    });
    
    // 应用所有模式
    patterns.forEach(pattern => {
        if (typeof pattern === 'string') {
            // 字符串匹配
            const regex = false ? 
                new RegExp(escapeRegExp(pattern), 'g') : 
                new RegExp(escapeRegExp(pattern), 'gi');
            result = result.replace(regex, match => `<span>${match}</span>`);
        } else {
            // 正则表达式匹配
            result = result.replace(pattern, match => `<span>${match}</span>`);
        }
    });
    
    return result;
}

// 转义正则表达式特殊字符
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// 添加到搜索历史
function addToHistory(query) {
    // 移除重复的查询
    searchHistory = searchHistory.filter(item => item.query !== query);
    
    // 添加新查询
    searchHistory.push({
        query: query,
    });
    
    // 限制历史记录数量
    if (searchHistory.length > 50) {
        searchHistory = searchHistory.slice(-50);
    }
    
    // 保存到本地存储
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
    
    // 重新渲染历史记录
    renderSearchHistory();
}

// 从搜索历史中移除
function removeFromHistory(query) {
    searchHistory = searchHistory.filter(item => item.query !== query);
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
    renderSearchHistory();
}

// 清除所有搜索历史
async function clearAllHistory() {
    const langs = await loadJson('./res/langs.json')
    const select_lang = localStorage.getItem('lang')

    if (confirm(getLang(langs, select_lang, '0e'))) {
        searchHistory = [];
        localStorage.removeItem('searchHistory');
        renderSearchHistory();
    }
}

// 添加事件监听器
async function addEventListeners() {  
    langs = await loadJson('./res/langs.json')
    const select_lang = localStorage.getItem('lang')

    // 输入框回车事件
    searchInput.addEventListener('keypress', (e) => async function() {
        if (e.key === 'Enter') {
            await search(searchInput.value);
        }
    });
    
    // 清除历史记录按钮
    clearHistoryBtn.addEventListener('click', clearAllHistory);
    
    // 清除搜索结果按钮
    clearResultsBtn.addEventListener('click', () => {
        searchInput.value = '';
        resultsContainer.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h3>${getLang(langs, select_lang, '09')}</h3>
                <p>${getLang(langs, select_lang, '0a')}</p>
            </div>
        `;
        resultsCount.textContent = `${getLang(langs, select_lang, '07')}0 ${getLang(langs, select_lang, '08')}`;
    });

    // 输入框聚焦时选择所有文本
    searchInput.addEventListener('focus', function() {
        this.select();
    });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initPage);