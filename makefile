product_version = "2.2.1"
command = python -m nuitka --remove-output --msvc=latest --company-name="xystudio" --copyright="Copyright ? 2025 xystudio" --trademarks="Copyright ? 2025 xystudio" --product-version=$(product_version) --standalone

clickmouse: gui/main.py
	$(command) --file-description="���������" --product-name="ClickMouse" --windows-icon-from-ico=gui/res/icons/clickmouse/icon.ico --include-data-dir=gui/res/=res/ --include-data-file=gui/key=key gui/main.py --file-version="2.3.0.10a1" --windows-console-mode="disable"
	$(command) --file-description="�����������װ����" --product-name="CmInit" --windows-icon-from-ico=gui/inst_res/icons/install.ico --file-version="1.0.0.0" gui/init.py --windows-console-mode="disable"
	$(command) --file-description="��չ����" --product-name="ExtensionTest" --file-version="1.0.0.0" tests/hello.py 

clickmouse_lib: setup.py
	python setup.py bdist_wheel
	python setup.py sdist

clean:
	del -s -q -f build\ clickmouse.egg-info cython\*.c