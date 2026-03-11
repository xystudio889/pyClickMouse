command = python -m nuitka --msvc=latest --remove-output --company-name="xystudio" --copyright="Copyright 2026 xystudio" --trademarks="xystudio" --product-version="3.2.0" --standalone --output-dir=dist/clickmouse/

main:
	echo Please run a build command, such as "make clickmouse".

clickmouse: gui/main.py
	$(command) --file-description="Clickmouse" --product-name="ClickMouse" --windows-icon-from-ico=gui/res/icons/clickmouse/icon.ico --include-data-dir=gui/res/=res/ --include-data-file=gui/key=key gui/main.py --file-version="3.2.0.19"  --enable-plugin=pyside6 --windows-console-mode="disable" --include-data-file=gui/7z.exe=7z.exe --include-data-file=gui/7z.dll=7z.dll
	$(command) --file-description="Clickmouse uninstall" --product-name="uninstall" --windows-icon-from-ico=gui/res/icons/clickmouse/uninstall.ico --file-version="2.1.4.7" gui/uninstall.py  --enable-plugin=pyside6 --windows-console-mode="disable" --windows-uac-admin
	$(command) --file-description="Clickmouse IPK" --product-name="CmIPK" --windows-icon-from-ico=gui/res/icons/clickmouse/init.ico --file-version="2.0.6.10" gui/install_pack.py  --enable-plugin=pyside6 --windows-console-mode="disable"
	$(command) --file-description="Clickmouse repair" --product-name="CmRepair" --windows-icon-from-ico=gui/res/icons/clickmouse/repair.ico --file-version="2.2.3.6" gui/repair.py  --enable-plugin=pyside6 --windows-console-mode="disable" --windows-uac-admin
	$(command) --file-version="1.0.1.3" gui/check_reg_ver.py  --windows-console-mode="disable"
	$(command) --file-version="1.0.0.2" gui/updater.py  --windows-console-mode="disable"
	powershell -ExecutionPolicy Bypass -Command "./merge-distFolders.ps1 -SourcePath ./dist/clickmouse/"

clickmouse_lib: setup.py
	python setup.py bdist_wheel
	python setup.py sdist
	mkpyd

extension:
	echo No extension!

clean_pyd:
	del -s -q -f build\ clickmouse.egg-info cython\*.c

gitclean:
	git gc --aggressive --prune=now

pyd:
	@echo off
	setlocal enabledelayedexpansion

	set items="38" "39" "310" "311" "312" "313" "314"

	for %%i in (%items%) do (
		"C:\Program Files\Python%%i\python.exe" cython\setup.py build_ext --inplace
	)

	set versions=3.13 3.14
	for %%v in (%versions%) do (
		set "orig=%%v"
		set "nodot=!orig:.=!"
		"C:\Program Files\Python!nodot!\python%!orig!t.exe" cython\setup.py build_ext --inplace
	)