# pdfebook

A tool to produce a PDF ebook from a cover image and interior PDF,
or a ZIP archive containing a PDF ebook and an EPUB.

Usage to produce just a PDF:

```bash
pdfebook --size A5 \
    --cover cover.jpg \
    --interior interior.pdf \
    --author "An Author" \
    --title "Title of Book"
    --outfile ebook.pdf
```

Or, if you have an EPUB, to create a ZIP file with both formats:

```bash
pdfebook --size 5.5x8.5 \
    --cover cover.jpg \
    --interior interior.jpg \
    --author "Quite N. Author" \
    --title "That Book" \
    --outfile "that_book.zip"
```

In the latter case, the resulting ZIP file will contain a directory,
`that_book`, itself containing files `that_book.pdf` and `that_book.epub`.
