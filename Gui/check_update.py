"""检查更新"""
from packaging.version import parse
from version import __version__
import requests
import keycrypter
from pathlib import Path
from sharelibs import get_lang, get_resource_path
import json
import certifi

def get_value_by_indices(data, indices_list):
    result = []
    for indices in indices_list:
        current = data
        for idx in indices:
            current = current[idx]
        result.append(current)
    return result

folder = Path(__file__).parent.resolve() # 获取资源文件夹

# 加载敏感信息
try:
    keys = keycrypter.decrypt()
    with open(get_resource_path('update.json'), 'r', encoding='utf-8') as f:
        keys_update = json.load(f)
except FileNotFoundError:
    keys = None
    keys_update = None

# 检察更新的函数
def get_version(website: str="github", include_prerelease: bool=False) -> str | None:
    """获取最新的版本号"""
    if keys is None:
        return get_lang('b2'), -1
    
    for i in keys_update:
        if i['website_name'] == website:
            web_data = i
            break
    else:
        return get_lang('b1'), -1
    
    try:
        web = web_data['api_web']
        headers = web_data['header']
        headers['Authorization'] = headers['Authorization'].format(keys[web_data['website_name']])
        else_data = web_data['addtional_info']
        releases_tag_condition = web_data['releases_tag_condition']
        condition = eval(web_data['condition'])
    except Exception as e:
        return e, -1
    
    try:
        # 获取版本号
        response = requests.get(web, headers=headers, **else_data)
        response.raise_for_status()
        release = response.json()
        if include_prerelease:
            releases = [r for r in release]
        else:
            releases = [r for r in release if not condition(r)]
        latest_tag = get_value_by_indices(releases, releases_tag_condition)
        return latest_tag
    except Exception as e:
        return e, -1

def check_update(
    use_website = "gitee",
    include_prerelease=False
):
    """检查更新"""
    # 获取版本号
    installed_version = __version__
    version = get_version(
        use_website, 
        include_prerelease,
    )
    latest_version = version[0]
    version_update_info = version[1]
    latest_version
    if version[1] == -1:
        # 出错
        return latest_version, -1, -1

    # 判断是否需要更新
    if latest_version:
        if installed_version == 'dev': 
            return False, latest_version, ''
        installed_parsed = parse(installed_version)
        latest_parsed = parse(latest_version)
        needs_update = installed_parsed < latest_parsed
    else:
        needs_update = False

    return needs_update, latest_version, version_update_info
