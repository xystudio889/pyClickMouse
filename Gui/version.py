"""读取版本号信息"""

def get_version():
    from pathlib import Path

    folder = Path(__file__).parent.resolve()

    with open(folder / "res" / "version", "r") as f:
        version = f.read()
    return version