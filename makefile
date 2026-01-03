command = python -m nuitka --remove-output --msvc=latest --company-name="xystudio" --copyright="Copyright ? 2025 xystudio" --trademarks="?xystudio?" --product-version="3.1.0" --standalone

clickmouse: gui/main.py
	$(command) --file-description="鼠标连点器" --product-name="ClickMouse" --windows-icon-from-ico=gui/res/icons/clickmouse/icon.ico --include-data-dir=gui/res/=res/ --include-data-file=gui/key=key --include-data-file=gui/dev.dat=dev.dat gui/main.py --file-version="3.1.0.14"  --enable-plugin=pyside6 --windows-console-mode="disable"
	$(command) --file-description="鼠标连点器安装程序" --product-name="CmInit" --windows-icon-from-ico=gui/res/icons/clickmouse/init.ico --file-version="2.0.0.0" gui/init.py  --enable-plugin=pyside6 --windows-console-mode="disable"
	$(command) --file-description="鼠标连点器卸载" --product-name="uninstall" --windows-icon-from-ico=gui/res/icons/clickmouse/uninstall.ico --file-version="2.0.0.0" gui/uninstall.py  --enable-plugin=pyside6 --windows-console-mode="disable"
	$(command) --file-description="鼠标连点器修改" --product-name="CmModify" --windows-icon-from-ico=gui/res/icons/clickmouse/init.ico --file-version="2.0.0.0" gui/install_pack.py  --enable-plugin=pyside6 --windows-console-mode="disable"
	$(command) --file-description="鼠标连点器修复" --product-name="CmRepair" --windows-icon-from-ico=gui/res/icons/clickmouse/repair.ico --file-version="2.0.0.0" gui/repair.py  --enable-plugin=pyside6 --windows-console-mode="disable"

clickmouse_lib: setup.py
	python setup.py bdist_wheel
	python setup.py sdist
	mkpyd

clean:
	del -s -q -f build\ clickmouse.egg-info cython\*.c
