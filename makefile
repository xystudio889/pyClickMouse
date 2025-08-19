file_version = "1.0.0.0"
product_version = "1.0.0"
name = "ClickMouse"
copyright = "Copyright © 2025 xystudio"

clickmouse: gui/main.py
	python -m nuitka --onefile --msvc=latest --windows-console-mode="disable" --windows-icon-from-ico=gui/res/icon.ico --include-data-dir=gui/res gui/main.py

clickmouse_lib: setup.py
	pip install .