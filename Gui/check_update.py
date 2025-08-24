"""检查更新"""
from packaging.version import parse
import version
import requests
import json
from pathlib import Path

__version__ = version.get_version() # 获取版本号
folder = Path(__file__).parent.resolve() / "res" # 获取资源文件夹

# 加载敏感信息
with open(folder / "key.json", "r") as f:
    keys = json.load(f)
# GITHUB_API_KEY = keys['GITHUB_API_KEY']
GITEE_API_KEY = keys['GITEE_API_KEY']

# 检察更新的函数
def get_latest_version(website: str="github", include_prerelease: bool=False, header: None | dict=None) -> str | None:
    """获取最新的版本号"""
    if GITEE_API_KEY is None:
        return "未设置GITEE_API_KEY，请配置res/key.json后再次编译", -1
    if website == "github":
        # 获取github的版本号
        pass
    elif website == "gitee":
        # 获取gitee的版本号
        web = "https://gitee.com/api/v5/repos/xystudio889/pyclickmouse/releases/"
        headers = {"Authorization": f"Bearer {GITEE_API_KEY}"}
    else:
        # 自定义的网站版本号
        web = website
        headers = header
    
    try:
        # 获取版本号
        response = requests.get(web, headers=headers)
        response.raise_for_status()
        release = response.json()
        if include_prerelease:
            releases = [r for r in release if r.get("prerelease", False)]
        else:
            releases = [r for r in release if not r.get("prerelease", False)]
        latest_tag = releases[0]["tag_name"]
        return latest_tag
    except requests.exceptions.RequestException as e:
        print(f"Network error:{e}")
        return e, -1
    except Exception as e:
        print("UnexpectedError: Failed to get latest version:{e}")
        return e, -1

def check_update(
    use_website = "gitee",
    include_prerelease=False
):
    """检查更新"""
    # 获取版本号
    installed_version = __version__
    latest_version = get_latest_version(
        use_website, 
        include_prerelease,
    )
    if isinstance(latest_version, tuple):
        return latest_version

    # 判断是否需要更新
    if latest_version:
        installed_parsed = parse(installed_version)
        latest_parsed = parse(latest_version)
        needs_update = installed_parsed < latest_parsed
    else:
        needs_update = False

    return needs_update, latest_version
