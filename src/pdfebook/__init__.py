"""
Script to convert an interior PDF plus cover image file to a PDF ebook.
May also include an EPUB file to create a ZIP archive with both EPUB and PDF.
"""

import functools
import importlib.metadata
import io
import re
import tempfile
import unicodedata
import zipfile

import click
import fpdf
import pypdf


__version__ = importlib.metadata.version("pdfebook")

__doc__ = f"""\
    pdfebook creates a PDF ebook from an interior PDF and a book cover image file.
    It can also produce a zip archive containing both an EPUB and PDF.
    
    version: {__version__}
    """
    
def assign_docstring(docstring):
    def decorator(func):
        func.__doc__ = docstring
        return func
    return decorator


def get_format(size: str):
    size = size.lower()
    if size in fpdf.fpdf.PAGE_FORMATS:
        return fpdf.fpdf.PAGE_FORMATS[size]
    return tuple(72 * float(x.strip()) for x in size.split("x", 1))


def get_format_from_pdf(pdf: str):
    reader = pypdf.PdfReader(pdf)
    first_page = reader.pages[0]
    return tuple(first_page.mediabox[2:])


def get_cover_pages(format, cover, is_back=False):
    pdf = fpdf.FPDF(format=format, unit="pt")
    pdf.set_margin(0)
    # We add a blank page either before (in the case of a back cover)
    # or after (in the case of the front)
    if is_back:
        pdf.add_page
    pdf.add_page()
    pdf.image(cover, h=pdf.eph, w=pdf.epw)
    if not is_back:
        pdf.add_page()
    return io.BytesIO(pdf.output())


def get_slug(title):
    title = (
        unicodedata.normalize("NFKD", str(title))
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    title = re.sub(r"[^\w\s-]", "", title.lower())
    return re.sub(r"[-\s]+", "_", title).strip("-_")


@click.command()
@click.option("-t", "--title", required=True, help="Title of book")
@click.option(
    "-a",
    "--author",
    required=True,
    help="Author(s) of book",
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
@click.option(
    "-b",
    "--back",
    default=None,
    type=click.Path(exists=True),
    help="Path to back cover image file",
)
@click.option("-p", "--epub", type=click.Path(exists=True), help="Path to epub file")
@click.option(
    "-s",
    "--size",
    default=None,
    help=(
        "Trim size of book: either a format name like 'A3', 'A4', 'A5', 'letter', "
        "or 'legal', or dimensions in inches formatted '<width>x<height>', e.g., '7x10' "
        "or '5.5x8.5' [default: inferred]"
    ),
)
@assign_docstring(__doc__)
def run(title, author, cover, interior, outfile, epub=None, back=None, size=None):
    if size is None:
        format = get_format_from_pdf(interior)
    else:
        format = get_format(size)
    writer = pypdf.PdfWriter()
    writer.append(get_cover_pages(format, cover))
    writer.append(interior)
    if back:
        writer.append(get_cover_pages(format, back, is_back=False))
    writer.add_metadata({"/Author": author, "/Title": title})
    if epub:
        slug = get_slug(title)
        with zipfile.ZipFile(outfile, "w") as archive:
            archive.mkdir(slug)
            archive.write(epub, arcname=f"{slug}/{slug}.epub")
            with io.BytesIO() as buffer:
                writer.write(buffer)
                archive.writestr(f"{slug}/{slug}.pdf", buffer.getvalue())
    else:
        writer.write(outfile)


run.__doc__ = __doc__

if __name__ == "__main__":
    run()
