"""
Script to convert an interior PDF plus cover image file to a PDF ebook.
"""

import datetime
import io

import click
import fpdf
import pypdf


def get_cover_pages(size, cover):
    pdf = fpdf.FPDF(format=size)
    pdf.set_margin(0)
    pdf.add_page()
    pdf.image(cover, h=pdf.eph, w=pdf.epw)
    # add blank page
    pdf.add_page()
    return io.BytesIO(pdf.output())


@click.command()
@click.option("-t", "--title", required=True)
@click.option("-a", "--author", required=True)
@click.option("-s", "--size", default="A5")
@click.option("-c", "--cover", required=True, type=click.Path(exists=True))
@click.option("-i", "--interior", required=True, type=click.Path(exists=True))
@click.option("-o", "--outfile", required=True, type=click.Path())
def run(title, author, size, cover, interior, outfile):
    buffer = get_cover_pages(size, cover)
    writer = pypdf.PdfWriter()
    writer.append(buffer)
    writer.append(interior)
    writer.add_metadata({"/Author": author, "/Title": title})
    writer.write(outfile)


if __name__ == "__main__":
    run()
