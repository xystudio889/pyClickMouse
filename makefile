command = python -m nuitka --msvc=latest --remove-output --company-name="xystudio" --copyright="Copyright 2026 xystudio" --trademarks="xystudio" --product-version="3.2.0" --standalone --output-dir=dist/clickmouse/

main:
	echo Please run a build command, such as "make clickmouse".

clickmouse: gui/main.py
	$(command) --file-description="Clickmouse" --product-name="ClickMouse" --windows-icon-from-ico=gui/res/icons/clickmouse/icon.ico --include-data-dir=gui/res/=res/ --include-data-file=gui/key=key --include-data-file=gui/dev.dat=dev.dat gui/main.py --file-version="3.2.0.18"  --enable-plugin=pyside6 --windows-console-mode="disable" --include-data-file=gui/7z.exe=7z.exe --include-data-file=gui/7z.dll=7z.dll
	$(command) --file-description="Clickmouse uninstall" --product-name="uninstall" --windows-icon-from-ico=gui/res/icons/clickmouse/uninstall.ico --file-version="2.1.4.7" gui/uninstall.py  --enable-plugin=pyside6 --windows-console-mode="disable" --windows-uac-admin
	$(command) --file-description="ClickMouse modify" --product-name="CmModify" --windows-icon-from-ico=gui/res/icons/clickmouse/init.ico --file-version="2.0.6.9" gui/install_pack.py  --enable-plugin=pyside6 --windows-console-mode="disable"
	$(command) --file-description="Clickmouse repair" --product-name="CmRepair" --windows-icon-from-ico=gui/res/icons/clickmouse/repair.ico --file-version="2.2.3.6" gui/repair.py  --enable-plugin=pyside6 --windows-console-mode="disable" --windows-uac-admin
	$(command) --file-version="1.0.1.2" gui/check_reg_ver.py  --windows-console-mode="disable" --enable-plugin=pyside6
	$(command) --file-version="1.0.0.1" gui/updater.py  --windows-console-mode="disable" --enable-plugin=pyside6

clickmouse_lib: setup.py
	python setup.py bdist_wheel
	python setup.py sdist
	mkpyd

extension:
	echo No extension!

clean:
	del -s -q -f build\ clickmouse.egg-info cython\*.c

gitclean:
	git gc --aggressive --prune=now

pyd:
	"C:\program files\python38\python.exe" cython/setup.py build_ext
	"C:\program files\python39\python.exe" cython/setup.py build_ext
	"C:\program files\python310\python.exe" cython/setup.py build_ext
	"C:\program files\python311\python.exe" cython/setup.py build_ext
	"C:\program files\python312\python.exe" cython/setup.py build_ext
	"C:\program files\python313\python.exe" cython/setup.py build_ext
	"C:\program files\python313\python3.13t.exe" cython/setup.py build_ext
	"C:\program files\python314\python.exe" cython/setup.py build_ext
	"C:\program files\python314\python3.14t.exe" cython/setup.py build_ext