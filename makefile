file_version = "2.2.0.7"
product_version = "2.2.0"
command = python -m nuitka --onefile --remove-output --msvc=latest --windows-console-mode="disable"  --company-name="xystudio" --copyright="Copyright ? 2025 xystudio" --trademarks="Copyright ? 2025 xystudio" --file-version="$(file_version)" --product-version="$(product_version)"

clickmouse: gui/main.py
	$(command) --file-description=" Û±Í¡¨µ„∆˜" --product-name="ClickMouse" --windows-icon-from-ico=gui/res/icons/icon.ico --include-data-file=gui/key.json=key.json gui/main.py

clickmouse_lib: setup.py
	python setup.py bdist_wheel
	python setup.py sdist

clean:
	del -s -q -f build\ clickmouse.egg-info cython\*.c