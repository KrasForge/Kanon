# Datasheet ingestion research (#35)

Decision: use native PDF text plus coordinates and table candidates as the first pass;
retain the original document hash and require independent review before promoting a
candidate into a verified constraint. OCR is a fallback for image-only pages and must
never be the sole authority for a numeric electrical limit.

The reproducible probe in `research/datasheet_probe.py` used PyMuPDF 1.28.2 against TI's
[OPA1655/OPA1656 datasheet](https://www.ti.com/lit/ds/symlink/opa1656.pdf), revision SBOS901C
(September 2022). The PDF stays outside the repository; `datasheet-probe.json` records
its SHA-256 and structural measurements. No datasheet body or vendor model is redistributed.
Run the script with a local PDF and `--output` to repeat against that exact document hash.

The probe found a 47×8 table on page 6 and a 9×7 table on page 7. Page 6 has 228 empty
extracted cells; these include intentionally blank/merged cells and **are not an error
rate**. Visual inspection of page 6 confirmed grouped parameters, conditional rows,
separate minimum/typical/maximum columns and units. Flattened reading order alone cannot
safely associate a number with its complete condition, limit type and footnotes. A table
of contents also matched the heading search, demonstrating that heading presence does
not identify a constraint table reliably.

[PyMuPDF text extraction](https://pymupdf.readthedocs.io/en/latest/recipes-text.html)
provides positioned text/words, while its [table API](https://pymupdf.readthedocs.io/en/latest/page.html)
can propose cell structures. These are extraction aids, not proof of transcription or
applicability. Keep text spans, page/crop coordinates, table headers, row context, units,
conditions, footnotes and document revision together in any candidate record.

A production evaluation corpus should include native-text datasheets, scans, rotated
pages, multipage tables, superscripts, min/typ/max columns, negative signs, μ/m prefixes,
absolute-maximum versus recommended-operation tables and temperature-dependent limits.
Label values and their context manually. Measure numeric/unit/condition association
accuracy separately, including abstention and revision-change behavior. Do not quote a
high character-extraction score as electrical accuracy. Supplier descriptions and snippets
must not override manufacturer documents.

Promotion boundary: unreviewed candidate → cited, condition-specific constraint →
independently accepted rule data. Store the acceptance outside the Designer's mutation
surface. `datasheets.Registry` and `SourcedLimit` already preserve file identity and
numeric units, but they do not implement candidate extraction, OCR, authenticity checking
or automatic acceptance. This probe does not establish a reliable unattended ingestion
pipeline; additional labeled-corpus evaluation is required before one is deployed.
