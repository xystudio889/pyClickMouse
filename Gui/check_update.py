"""检查更新"""
from packaging.version import parse
from version import __version__
import requests
import xQklN2n
from pathlib import Path

folder = Path(__file__).parent.resolve() # 获取资源文件夹

# 加载敏感信息
try:
    keys = eval(''.join(chr((ord(c) - 129 + 137) % 128) for c in 'pIcdF*f&:p*qL0e !'))
    GITHUB_API_KEY = keys['GITHUB_API_KEY']
    GITEE_API_KEY = keys['GITEE_API_KEY']
except FileNotFoundError:
    GITEE_API_KEY = None
    GITHUB_API_KEY = None

# 检察更新的函数
def get_version(website: str="github", include_prerelease: bool=False, header: None | dict=None, condition: callable = lambda x: x.get("prerelease", False), release_tag_condition:tuple[int, str] = (-1, "tag_name", "body")) -> str | None:
    """获取最新的版本号"""
    if website == "github":
        # 检查是否设置GITHUB_API_KEY
        if GITHUB_API_KEY is None:
            return "未设置GITEE_API_KEY，请配置res/key.json后再次编译", -1
        # 获取github的版本号
        web = "https://api.github.com/repos/xystudio889/pyclickmouse/releases"
        headers = {"Authorization": f"token {GITHUB_API_KEY}"}
        else_data = {"verify": False}
        condition = lambda x: x.get("prerelease", False)
        release_tag_condition = (-1, "tag_name", "body")
    elif website == "gitee":
        # 检查是否设置GITEE_API_KEY
        if GITEE_API_KEY is None:
            return "未设置GITEE_API_KEY，请配置res/key.json后再次编译", -1
        if GITEE_API_KEY == -1:
            return "未找到res/key.json文件，请配置res/key.json后再次编译", -1
        # 获取gitee的版本号
        web = "https://gitee.com/api/v5/repos/xystudio889/pyclickmouse/releases/"
        headers = {"Authorization": f"Bearer {GITEE_API_KEY}"}
        else_data = {}
        release_tag_condition = (-1, "name", "body")
    else:
        # 自定义的网站版本号
        web = website
        headers = header
    try:
        # 获取版本号
        response = requests.get(web, headers=headers, **else_data)
        response.raise_for_status()
        release = response.json()
        if include_prerelease:
            releases = [r for r in release if condition(r)]
        else:
            releases = [r for r in release if not condition(r)]
        latest_tag = releases[release_tag_condition[0]][release_tag_condition[1]], releases[release_tag_condition[0]][release_tag_condition[2]]
        return latest_tag
    except requests.exceptions.RequestException as e:
        return e, -1
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
        installed_parsed = parse(installed_version)
        latest_parsed = parse(latest_version)
        needs_update = installed_parsed < latest_parsed
    else:
        needs_update = False

    return needs_update, latest_version, version_update_info
