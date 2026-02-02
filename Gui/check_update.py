'''检查更新'''
from packaging.version import parse
import requests
import keycrypter
from pathlib import Path
from sharelibs import get_lang, get_resource_path, __version__
import json
from traceback import format_exc

def get_value_by_indices(data, indices_list):
    result = []
    for indices in indices_list:
        current = data
        for idx in indices:
            if isinstance(idx, str):
                if idx.endswith('+'):
                    current = current[int(idx[:-1]):] # 切片
                else:
                    current = current[idx]
            else:
                current = current[idx]
        result.append(current)
    return result

folder = Path(__file__).parent.resolve() # 获取资源文件夹

# 加载敏感信息
try:
    with open('key') as f:
        key = f.read()
    keys = keycrypter.decrypt(key)
    with open(get_resource_path('update.json'), 'r', encoding='utf-8') as f:
        keys_update = json.load(f)
        
    for i in keys_update:
        if i['website_name'] == 'github': # TODO:这是临时方案，后续需要改为读取设置
            web_data = i
            break
    else:
        web_data = None
except FileNotFoundError:
    keys = None
    keys_update = None

# 检察更新的函数
def get_version(website: str='github', include_prerelease: bool=False) -> str | None:
    '''获取最新的版本号'''
    if keys is None:
        return get_lang('b2'), -1
    if web_data is None:
        return get_lang('b1'), -1
    
    try:
        web = web_data['api_web']
        headers = web_data['header']
        headers['Authorization'] = headers['Authorization'].format(keys[web_data['website_name']])
        else_data = web_data['addtional_info']
        releases_tag_condition = web_data['releases_tag_condition']
        condition = eval(web_data['condition'])
    except Exception as e:
        return format_exc(), -1
    
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
        return format_exc(), -1, -1

def check_update(
    use_website = 'github',
    include_prerelease=False
):
    '''检查更新'''
    # 获取版本号
    installed_version = __version__
    version = get_version(
        use_website, 
        include_prerelease,
    )
    latest_version = version[0]
    version_update_info = version[1]
    version_data = version[2]
    latest_version
    if version_update_info == -1:
        # 出错
        return latest_version, -1, -1
    
    # 获取哈希
    if web_data['has_hash']:
        for i in get_value_by_indices(version_data, [web_data['hash_data']['condition_list'][0]])[0]: # 获取最新版本的资源数据
            if get_value_by_indices(i, [web_data['hash_data']['condition_list'][1]])[0] == web_data['hash_data']['bin_name']: # 查找最新版本的正确资源
                hash_data = [get_value_by_indices(i, [web_data['hash_data']['condition_list'][2]])[0], web_data['hash_data']['hash_type']] # 获取哈希数据
                break
        else:
            hash_data = None
    else:
        hash_data = None

    # 判断是否需要更新
    if latest_version:
        if installed_version == 'dev': 
            return False, latest_version, ''
        installed_parsed = parse(installed_version)
        latest_parsed = parse(latest_version)
        needs_update = installed_parsed < latest_parsed
    else:
        needs_update = False

    return needs_update, latest_version, version_update_info, hash_data

def download_file(url, save_path):
    '''
    下载
    '''
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        return True, ''
    except Exception:
        return False, format_exc()
