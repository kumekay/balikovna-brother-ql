# Print Balikovna/Czech Post labels on Brother QL printer with 62 mm paper.


I do have Brother QL-600 Label Printer and sometimes I need to print labels for Czech Post which are 1/4 of A4.


So this script is the solution.


To print:

```
uv run main.py Stitek_na_balik.pdf
uv run brother_ql -m QL-600 -p usb://0x04f9:0x20c0 print -l 62 -r 90  Stitek_na_balik_top.png
uv run brother_ql -m QL-600 -p usb://0x04f9:0x20c0 print -l 62 -r 90  Stitek_na_balik_bottom.png
```

## USB Permissions (udev rule)

If you get `Access denied (insufficient permissions)` when trying to print, create a udev rule:

```bash
sudo tee /etc/udev/rules.d/99-brother-ql.rules << 'EOF'
SUBSYSTEM=="usb", ATTR{idVendor}=="04f9", ATTR{idProduct}=="20c0", MODE="0666"
EOF
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Then unplug and replug the printer.
