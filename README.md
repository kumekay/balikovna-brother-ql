# Print Balikovna/Czech Post labels on Brother QL printer with 62 mm paper.

I do have Brother QL-600 Label Printer and sometimes I need to print labels for Czech Post which are 1/4 of A4.

So this script is the solution.

## Usage

To print directly:

```
uv run main.py Stitek_na_balik.pdf
```

To only extract images (without printing):

```
uv run main.py --no-print Stitek_na_balik.pdf

# And then print them manually:
uv run brother_ql -m QL-600 -p usb://0x04f9:0x20c0 print -l 62 -r 90  Stitek_na_balik_top.png
```

## Configuration

Configure via CLI arguments or environment variables:

| Option | Env Variable | Default |
|--------|--------------|---------|
| `-m, --model` | `BROTHER_QL_MODEL` | `QL-600` |
| `-p, --printer` | `BROTHER_QL_PRINTER` | `usb://0x04f9:0x20c0` |
| `-l, --label` | `BROTHER_QL_LABEL` | `62` |

Example with custom printer:

```
uv run main.py -m QL-800 -p usb://0x04f9:0x209b Stitek_na_balik.pdf
```

Or via environment:

```
export BROTHER_QL_MODEL=QL-800
export BROTHER_QL_PRINTER=usb://0x04f9:0x209b
uv run main.py Stitek_na_balik.pdf
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
