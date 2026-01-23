command = python -m nuitka --remove-output --msvc=latest --company-name="xystudio" --copyright="Copyright 2026 xystudio" --trademarks="xystudio" --product-version="3.1.2" --standalone

clickmouse: gui/main.py
	$(command) --file-description="Clickmouse" --product-name="ClickMouse" --windows-icon-from-ico=gui/res/icons/clickmouse/icon.ico --include-data-dir=gui/res/=res/ --include-data-file=gui/key=key --include-data-file=gui/dev.dat=dev.dat gui/main.py --file-version="3.1.1.16"  --enable-plugin=pyside6 --windows-console-mode="disable" --output-dir=bin/
	$(command) --file-description="Clickmouse install" --product-name="CmInit" --windows-icon-from-ico=gui/res/icons/clickmouse/init.ico --file-version="2.1.5.8" gui/init.py  --enable-plugin=pyside6 --windows-console-mode="disable" --windows-uac-admin --output-dir=bin/
	$(command) --file-description="Clickmouse uninstall" --product-name="uninstall" --windows-icon-from-ico=gui/res/icons/clickmouse/uninstall.ico --file-version="2.1.4.7" gui/uninstall.py  --enable-plugin=pyside6 --windows-console-mode="disable" --windows-uac-admin --output-dir=bin/
	$(command) --file-description="ClickMouse modify" --product-name="CmModify" --windows-icon-from-ico=gui/res/icons/clickmouse/init.ico --file-version="2.0.5.6" gui/install_pack.py  --enable-plugin=pyside6 --windows-console-mode="disable" --output-dir=bin/
	$(command) --file-description="Clickmouse repair" --product-name="CmRepair" --windows-icon-from-ico=gui/res/icons/clickmouse/repair.ico --file-version="2.2.2.5" gui/repair.py  --enable-plugin=pyside6 --windows-console-mode="disable" --windows-uac-admin --output-dir=bin/
	$(command) --file-version="1.0.1.1" gui/check_reg_ver.py  --windows-console-mode="disable" --output-dir=bin/ --enable-plugin=pyside6

clickmouse_lib: setup.py
	python setup.py bdist_wheel
	python setup.py sdist
	mkpyd

clean:
	del -s -q -f build\ clickmouse.egg-info cython\*.c
