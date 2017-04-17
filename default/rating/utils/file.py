from django.utils import encoding
import codecs


def read_uploaded_file(f):
    lines = list()
    with f:
        for line in f:
            if line.startswith(codecs.BOM_UTF8):
                line = line.replace(codecs.BOM_UTF8, '')
            ok, s = __try_decode(line.strip(), "UTF-8", "cp1251")
            if ok and s:
                lines.append(s)
    return lines


def __try_decode(s, *encodings):
    for enc in encodings:
        try:
            decoded = encoding.force_text(s, encoding=enc, strings_only=True)
            return True, decoded
        except UnicodeDecodeError:
            pass
    return False, s
