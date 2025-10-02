product_version = "2.2.1"
command = python -m nuitka --remove-output --msvc=latest --windows-console-mode="disable" --company-name="xystudio" --copyright="Copyright ? 2025 xystudio" --trademarks="Copyright ? 2025 xystudio" --product-version=$(product_version)

clickmouse: gui/main.py
	$(command) --file-description="鼠标连点器" --product-name="ClickMouse" --windows-icon-from-ico=gui/res/icons/clickmouse/icon.ico --include-data-dir=gui/res/=res/ --include-data-file=gui/key=key gui/main.py --file-version="2.2.1.8" --standalone

installer: gui/init.py
	$(command) --file-description="鼠标连点器安装程序" --product-name="ClickMouse" --windows-icon-from-ico=gui/res/icons/unis.ico gui/inst_res/icons/install.ico --file-version="1.0.0.0" --onefile

uninstaller:gui/uninstall.py
	$(command) --file-description="鼠标连点器卸载程序" --product-name="ClickMouse" --windows-icon-from-ico=gui/res/icons/unis.ico gui/uninstall.py --file-version="1.0.0.0" --enable-plugin=tk-inter --onefile

clickmouse_lib: setup.py
	python setup.py bdist_wheel
	python setup.py sdist

clean:
	del -s -q -f build\ clickmouse.egg-info cython\*.c