import argparse
import os
import sys
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster

DEFAULT_PRINTER_MODEL = os.environ.get("BROTHER_QL_MODEL", "QL-600")
DEFAULT_PRINTER_IDENTIFIER = os.environ.get("BROTHER_QL_PRINTER", "usb://0x04f9:0x20c0")
DEFAULT_LABEL_SIZE = os.environ.get("BROTHER_QL_LABEL", "62")


def extract_label_images(pdf_path: str) -> tuple[Image.Image, Image.Image]:
    """
    Extract the top-left quarter of the first page of a PDF,
    then split it into top and bottom halves.

    Args:
        pdf_path: Path to the input PDF file

    Returns:
        Tuple of PIL Images (top_half, bottom_half)
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    page = doc[0]

    page_rect = page.rect
    page_width = page_rect.width
    page_height = page_rect.height

    quarter_rect = fitz.Rect(0, 0, page_width / 2, page_height / 2)

    zoom = 300 / 72
    mat = fitz.Matrix(zoom, zoom)

    pix = page.get_pixmap(matrix=mat, clip=quarter_rect)

    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    img_width, img_height = img.size
    cut_height = int(img_height / 1.7)

    top_part = img.crop((0, 0, img_width, cut_height))
    bottom_part = img.crop((0, cut_height, img_width, img_height))

    padded_bottom = Image.new("RGB", (top_part.width, top_part.height), (255, 255, 255))
    padded_bottom.paste(bottom_part, (0, 0))
    bottom_part = padded_bottom

    doc.close()

    return top_part.rotate(-90, expand=True), bottom_part.rotate(-90, expand=True)


def print_image(
    img: Image.Image, label_name: str, model: str, printer: str, label: str
) -> None:
    """Print a single image to the Brother QL printer."""
    qlr = BrotherQLRaster(model)
    convert(qlr, [img], label, cut=True)
    send(qlr.data, printer)
    print(f"Printed: {label_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract and print Balikovna labels from PDF on Brother QL printer."
    )
    parser.add_argument(
        "pdf_file",
        help="Path to the input PDF file (A4, processes only the first page)",
    )
    parser.add_argument(
        "--no-print",
        action="store_true",
        help="Only extract images, don't print",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Directory to save output images (only used with --no-print)",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=DEFAULT_PRINTER_MODEL,
        help=f"Printer model (default: {DEFAULT_PRINTER_MODEL}, env: BROTHER_QL_MODEL)",
    )
    parser.add_argument(
        "-p",
        "--printer",
        default=DEFAULT_PRINTER_IDENTIFIER,
        help=f"Printer identifier (default: {DEFAULT_PRINTER_IDENTIFIER}, env: BROTHER_QL_PRINTER)",
    )
    parser.add_argument(
        "-l",
        "--label",
        default=DEFAULT_LABEL_SIZE,
        help=f"Label size (default: {DEFAULT_LABEL_SIZE}, env: BROTHER_QL_LABEL)",
    )

    args = parser.parse_args()

    try:
        top_img, bottom_img = extract_label_images(args.pdf_file)

        if args.no_print:
            pdf_path = Path(args.pdf_file)
            output_dir = Path(args.output_dir) if args.output_dir else pdf_path.parent
            output_dir.mkdir(parents=True, exist_ok=True)

            base_name = pdf_path.stem
            top_path = output_dir / f"{base_name}_top.png"
            bottom_path = output_dir / f"{base_name}_bottom.png"

            top_img.rotate(90, expand=True).save(top_path)
            bottom_img.rotate(90, expand=True).save(bottom_path)
            print(f"Saved: {top_path}")
            print(f"Saved: {bottom_path}")
        else:
            print_image(top_img, "top label", args.model, args.printer, args.label)
            print_image(bottom_img, "bottom label", args.model, args.printer, args.label)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
