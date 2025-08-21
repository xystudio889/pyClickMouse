file_version = "1.0.0.0"
product_version = "1.0.0"

clickmouse: gui/main.py
	python -m nuitka --onefile --remove-output --msvc=latest --windows-console-mode="disable"  --company-name="xystudio" --file-description=" Û±Í¡¨µ„∆˜" --file-version="$(file_version)" --product-version="$(product_version)" --product-name="ClickMouse" --copyright="Copyright ? 2025 xystudio" --trademarks="?xystudio?"  --windows-icon-from-ico=gui/res/icons/icon.ico --include-data-dir=gui/res=res gui/main.py

clickmouse_lib: setup.py
	python -m build