from functools import cache

from pypdf import PdfReader

from artefact.data import DATA_DIR


@cache
def load_policies() -> str:
    # Layout mode keeps sentences, bullets and tables readable, the default mode splits every word
    reader = PdfReader(DATA_DIR / "políticas_da_loja.pdf")
    lines = []
    for page in reader.pages:
        for line in page.extract_text(extraction_mode="layout").splitlines():
            line = line.rstrip()
            is_blank = line == ""
            previous_is_blank = len(lines) > 0 and lines[-1] == ""
            # Pages are padded with many blank lines, keep at most one in a row
            if is_blank and previous_is_blank:
                continue
            lines.append(line)
    return "\n".join(lines)
