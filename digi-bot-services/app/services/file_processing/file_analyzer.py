# file_analyzer.py
import os, io, csv, json, zipfile, mimetypes
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List, Tuple

# Optional deps guarded at runtime
try:
    from pypdf import PdfReader  # pip install pypdf
except Exception:
    PdfReader = None

try:
    import docx  # python-docx
except Exception:
    docx = None

try:
    import pptx  # python-pptx
except Exception:
    pptx = None

try:
    import openpyxl  # pip install openpyxl
except Exception:
    openpyxl = None

try:
    from PIL import Image  # pip install pillow
except Exception:
    Image = None

try:
    import pytesseract  # pip install pytesseract ; brew install tesseract
except Exception:
    pytesseract = None


@dataclass
class AnalyzeLimits:
    max_bytes: int = 25 * 1024 * 1024  # 25 MB
    max_pdf_pages: int = 1000
    max_slides: int = 1000
    max_cells: int = 200_000  # xlsx safety cap
    ocr_enabled: bool = False  # opt-in


SUPPORTED_EXTS = {
    # texty
    ".txt", ".md", ".csv", ".tsv", ".json", ".log",
    # docs
    ".pdf", ".docx", ".pptx", ".xlsx",
    # code
    ".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".go", ".rs", ".sh",
    ".sql", ".yaml", ".yml", ".xml",
    # images (optional OCR)
    ".png", ".jpg", ".jpeg", ".webp",
}

TEXT_EXTS = {".txt", ".md", ".log", ".html", ".css", ".py", ".js", ".ts", ".java",
             ".c", ".cpp", ".go", ".rs", ".sh", ".sql", ".yaml", ".yml", ".xml"}

@dataclass
class AnalyzeResult:
    ok: bool
    text: str
    meta: Dict[str, Any]
    warning: Optional[str] = None
    error: Optional[str] = None


class FileAnalyzer:
    def __init__(self, limits: Optional[AnalyzeLimits] = None):
        self.limits = limits or AnalyzeLimits()

    def analyze_path(self, path: str) -> AnalyzeResult:
        name = os.path.basename(path)
        ext = os.path.splitext(name)[1].lower()

        if ext not in SUPPORTED_EXTS:
            return AnalyzeResult(
                ok=False, text="", meta={"name": name, "ext": ext},
                error=f"Unsupported extension {ext}. Allowed: {sorted(SUPPORTED_EXTS)}"
            )

        size = os.path.getsize(path)
        if size > self.limits.max_bytes:
            return AnalyzeResult(
                ok=False, text="", meta={"name": name, "ext": ext, "bytes": size},
                error=f"File too large ({size} bytes). Max {self.limits.max_bytes}."
            )

        try:
            if ext in TEXT_EXTS:
                text = self._read_text_file(path)
                return AnalyzeResult(ok=True, text=text, meta=self._meta(name, ext, size))

            if ext in {".csv", ".tsv"}:
                text = self._read_csv(path, delimiter=("\t" if ext == ".tsv" else ","))
                return AnalyzeResult(ok=True, text=text, meta=self._meta(name, ext, size))

            if ext == ".json":
                text = self._read_json(path)
                return AnalyzeResult(ok=True, text=text, meta=self._meta(name, ext, size))

            if ext == ".pdf":
                return self._read_pdf(path, name, ext, size)

            if ext == ".docx":
                return self._read_docx(path, name, ext, size)

            if ext == ".pptx":
                return self._read_pptx(path, name, ext, size)

            if ext == ".xlsx":
                return self._read_xlsx(path, name, ext, size)

            if ext in {".png", ".jpg", ".jpeg", ".webp"}:
                return self._read_image(path, name, ext, size)

            # Fallback (shouldn't reach here)
            with open(path, "rb") as f:
                data = f.read()
            return AnalyzeResult(
                ok=True, text=data.decode("utf-8", errors="replace"),
                meta=self._meta(name, ext, size), warning="Used raw decode fallback."
            )

        except Exception as e:
            return AnalyzeResult(
                ok=False, text="", meta=self._meta(name, ext, size),
                error=f"Failed to analyze: {e}"
            )

    # ----------------------
    # Handlers
    # ----------------------
    def _read_text_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def _read_csv(self, path: str, delimiter: str = ",") -> str:
        out = io.StringIO()
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            r = csv.reader(f, delimiter=delimiter)
            for row in r:
                out.write("\t".join(row) + "\n")
        return out.getvalue()

    def _read_json(self, path: str) -> str:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
        # pretty-print compactly (avoid huge dumps)
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"), indent=2)

    def _read_pdf(self, path: str, name: str, ext: str, size: int) -> AnalyzeResult:
        if PdfReader is None:
            return AnalyzeResult(ok=False, text="", meta=self._meta(name, ext, size),
                                 error="pypdf not installed. pip install pypdf")
        reader = PdfReader(path)
        pages = len(reader.pages)
        cap = min(pages, self.limits.max_pdf_pages)
        parts = []
        for i in range(cap):
            try:
                parts.append(reader.pages[i].extract_text() or "")
            except Exception:
                parts.append("")  # keep going
        warning = None
        if pages > cap:
            warning = f"PDF truncated at {cap}/{pages} pages."
        return AnalyzeResult(ok=True, text="\n\n".join(parts),
                             meta=self._meta(name, ext, size, pages=pages), warning=warning)

    def _read_docx(self, path: str, name: str, ext: str, size: int) -> AnalyzeResult:
        if docx is None:
            return AnalyzeResult(ok=False, text="", meta=self._meta(name, ext, size),
                                 error="python-docx not installed. pip install python-docx")
        d = docx.Document(path)
        paras = [p.text for p in d.paragraphs]
        return AnalyzeResult(ok=True, text="\n".join(paras),
                             meta=self._meta(name, ext, size, paragraphs=len(paras)))

    def _read_pptx(self, path: str, name: str, ext: str, size: int) -> AnalyzeResult:
        if pptx is None:
            return AnalyzeResult(ok=False, text="", meta=self._meta(name, ext, size),
                                 error="python-pptx not installed. pip install python-pptx")
        pres = pptx.Presentation(path)
        slides = len(pres.slides)
        cap = min(slides, self.limits.max_slides)
        parts = []
        for i, slide in enumerate(pres.slides):
            if i >= cap:
                break
            texts = []
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    texts.append(shape.text)
            parts.append(f"[Slide {i+1}]\n" + "\n".join(texts))
        warning = None
        if slides > cap:
            warning = f"PPTX truncated at {cap}/{slides} slides."
        return AnalyzeResult(ok=True, text="\n\n".join(parts),
                             meta=self._meta(name, ext, size, slides=slides), warning=warning)

    def _read_xlsx(self, path: str, name: str, ext: str, size: int) -> AnalyzeResult:
        if openpyxl is None:
            return AnalyzeResult(ok=False, text="", meta=self._meta(name, ext, size),
                                 error="openpyxl not installed. pip install openpyxl")
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        total_cells = 0
        parts = []
        for ws in wb.worksheets:
            rows = []
            for row in ws.iter_rows(values_only=True):
                cells = ["" if v is None else str(v) for v in row]
                total_cells += len(cells)
                if total_cells > self.limits.max_cells:
                    parts.append("[Truncated: cell limit reached]")
                    warning = f"XLSX truncated after ~{self.limits.max_cells} cells."
                    text = f"[Sheet {ws.title}]\n" + "\n".join(rows)
                    return AnalyzeResult(ok=True, text=text, meta=self._meta(name, ext, size, sheets=len(wb.worksheets)),
                                         warning=warning)
                rows.append("\t".join(cells))
            parts.append(f"[Sheet {ws.title}]\n" + "\n".join(rows))
        return AnalyzeResult(ok=True, text="\n\n".join(parts),
                             meta=self._meta(name, ext, size, sheets=len(wb.worksheets)))

    def _read_image(self, path: str, name: str, ext: str, size: int) -> AnalyzeResult:
        if not self.limits.ocr_enabled:
            return AnalyzeResult(
                ok=True, text="",
                meta=self._meta(name, ext, size, ocr=False),
                warning="Image loaded. OCR disabled; enable limits.ocr_enabled=True to extract text."
            )
        if Image is None or pytesseract is None:
            return AnalyzeResult(
                ok=False, text="", meta=self._meta(name, ext, size),
                error="OCR not available. Install pillow & pytesseract and make sure Tesseract is installed."
            )
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        return AnalyzeResult(ok=True, text=text, meta=self._meta(name, ext, size, ocr=True))

    def _meta(self, name: str, ext: str, size: int, **extra) -> Dict[str, Any]:
        mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
        base = {"name": name, "ext": ext, "bytes": size, "mime": mime}
        base.update(extra)
        return base
