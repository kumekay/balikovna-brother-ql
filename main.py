import argparse
import sys
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image


def extract_top_left_quarter(
    pdf_path: str, output_dir: str | None = None
) -> tuple[str, str]:
    """
    Extract the top-left quarter of the first page of a PDF,
    then split it into top and bottom halves, saving as two image files.

    Args:
        pdf_path: Path to the input PDF file
        output_dir: Directory to save output files (defaults to same dir as PDF)

    Returns:
        Tuple of paths to the two output image files (top_half, bottom_half)
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if output_dir is None:
        output_dir = pdf_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Open the PDF and get the first page
    doc = fitz.open(pdf_path)
    page = doc[0]

    # Get page dimensions
    page_rect = page.rect
    page_width = page_rect.width
    page_height = page_rect.height

    # Define the top-left quarter (half width, half height)
    quarter_rect = fitz.Rect(0, 0, page_width / 2, page_height / 2)

    # Render the quarter at high resolution (300 DPI)
    # The matrix scales the rendering
    zoom = 300 / 72  # 72 is default DPI, we want 300 DPI
    mat = fitz.Matrix(zoom, zoom)

    # Clip to the quarter region
    pix = page.get_pixmap(matrix=mat, clip=quarter_rect)

    # Convert to PIL Image
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # Split into top and bottom halves
    img_width, img_height = img.size
    cut_height = int(img_height / 1.7)

    top_part = img.crop((0, 0, img_width, cut_height))
    bottom_part = img.crop((0, cut_height, img_width, img_height))

    # Pad bottom_part with white to match top_part height
    padded_bottom = Image.new("RGB", (top_part.width, top_part.height), (255, 255, 255))
    padded_bottom.paste(bottom_part, (0, 0))
    bottom_part = padded_bottom

    # Generate output filenames
    base_name = pdf_path.stem
    top_path = output_dir / f"{base_name}_top.png"
    bottom_path = output_dir / f"{base_name}_bottom.png"

    # Save the images
    top_part.save(top_path)
    bottom_part.save(bottom_path)

    doc.close()

    print(f"Saved top half: {top_path}")
    print(f"Saved bottom half: {bottom_path}")

    return str(top_path), str(bottom_path)


def main():
    parser = argparse.ArgumentParser(
        description="Extract top-left quarter of a PDF page and split into two halves."
    )
    parser.add_argument(
        "pdf_file",
        help="Path to the input PDF file (A4, processes only the first page)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Directory to save output images (defaults to same directory as PDF)",
    )

    args = parser.parse_args()

    try:
        extract_top_left_quarter(args.pdf_file, args.output_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing PDF: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
