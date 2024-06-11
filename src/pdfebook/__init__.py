"""
Script to convert an interior PDF plus cover image file to a PDF ebook.
"""

import io

import click
import fpdf
import pypdf


def get_format(size: str):
    size = size.lower()
    if size in fpdf.fpdf.PAGE_FORMATS:
        return fpdf.fpdf.PAGE_FORMATS[size]
    return tuple(72 * float(x.strip()) for x in size.split("x", 1))


def get_cover_pages(size, cover):
    format = get_format(size)
    pdf = fpdf.FPDF(format=format, unit="pt")
    pdf.set_margin(0)
    pdf.add_page()
    pdf.image(cover, h=pdf.eph, w=pdf.epw)
    # add blank page
    pdf.add_page()
    return io.BytesIO(pdf.output())


@click.command()
@click.option("-t", "--title", required=True, help="Title of book")
@click.option(
    "-a",
    "--author",
    required=True,
    help="Author(s) of book",
)
@click.option(
    "-s",
    "--size",
    default="A5",
    help=(
        "Trim size of book: either a format name like 'A3', 'A4', 'A5', 'letter', "
        "or 'legal', or dimensions in inches formatted '<width>x<height>', e.g., '7x10' "
        "or '5.5x8.5' [default: 'A5']"
    ),
)
@click.option(
    "-c",
    "--cover",
    required=True,
    type=click.Path(exists=True),
    help="Path to a cover image file",
)
@click.option(
    "-i",
    "--interior",
    required=True,
    type=click.Path(exists=True),
    help="Path to PDF of interior",
)
@click.option(
    "-o",
    "--outfile",
    required=True,
    type=click.Path(),
    help="Path to generated output",
)
def run(title, author, size, cover, interior, outfile):
    buffer = get_cover_pages(size, cover)
    writer = pypdf.PdfWriter()
    writer.append(buffer)
    writer.append(interior)
    writer.add_metadata({"/Author": author, "/Title": title})
    writer.write(outfile)


if __name__ == "__main__":
    run()
