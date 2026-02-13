#!/usr/bin/env python3
"""Extract structured text from PDFs into markdown files."""

import os, re, time, traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from pypdf import PdfReader

ARCHIVE = Path("/Users/kirane/projects/idp/docs/archive")
REFERENCE = Path("/Users/kirane/projects/idp/OpenAM-12-Reference.pdf")
OUTPUT = Path("/Users/kirane/projects/idp/docs/extracts/pdf")
ERROR_LOG = OUTPUT / "extraction-errors.md"
MAX_OUTPUT_LINES = 2000
MAX_WORKERS = 6


def sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-.]', '-', name).strip('-')


def title_from_filename(pdf_path: Path) -> str:
    stem = pdf_path.stem
    title = re.sub(r'[-_]+', ' ', stem)
    return title.title()


def classify_pdf_path(pdf_path: Path) -> tuple:
    try:
        rel = pdf_path.relative_to(ARCHIVE)
        parts = rel.parts
        if len(parts) >= 3:
            return parts[0], parts[1], pdf_path.stem
        elif len(parts) == 2:
            return parts[0], "unknown", pdf_path.stem
        else:
            return "misc", "unknown", pdf_path.stem
    except ValueError:
        return "openam", "12", pdf_path.stem


def detect_headings(text: str) -> list:
    headings = []
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r'^\d+(\.\d+)*\s+[A-Z]', stripped):
            headings.append(stripped)
        elif re.match(r'^(Chapter|Appendix|Part|Section)\s+\d', stripped, re.IGNORECASE):
            headings.append(stripped)
        elif stripped.isupper() and 3 < len(stripped) < 80:
            headings.append(stripped)
    return headings


def extract_tables_pdfplumber(pdf_path: Path, page_indices: list) -> list:
    try:
        import pdfplumber
    except ImportError:
        return []
    tables_md = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for idx in page_indices:
                if idx >= len(pdf.pages):
                    continue
                page = pdf.pages[idx]
                page_tables = page.extract_tables()
                if not page_tables:
                    continue
                for table in page_tables:
                    if not table or len(table) < 2:
                        continue
                    md_rows = []
                    header = table[0]
                    header_cells = [str(c).replace('\n', ' ').strip() if c else '' for c in header]
                    md_rows.append('| ' + ' | '.join(header_cells) + ' |')
                    md_rows.append('| ' + ' | '.join(['---'] * len(header_cells)) + ' |')
                    for row in table[1:]:
                        cells = [str(c).replace('\n', ' ').strip() if c else '' for c in row]
                        while len(cells) < len(header_cells):
                            cells.append('')
                        cells = cells[:len(header_cells)]
                        md_rows.append('| ' + ' | '.join(cells) + ' |')
                    tables_md.append('\n'.join(md_rows))
    except Exception:
        pass
    return tables_md


def find_table_pages(text_by_page: list) -> list:
    table_pages = []
    for i, text in enumerate(text_by_page):
        table_indicators = 0
        for line in text.split('\n'):
            if re.search(r'\S\s{3,}\S.*\S\s{3,}\S', line):
                table_indicators += 1
            if '|' in line and line.count('|') >= 2:
                table_indicators += 1
        if table_indicators >= 3:
            table_pages.append(i)
    return table_pages


def summarize_dense_text(text: str, max_lines: int) -> str:
    lines = text.split('\n')
    if len(lines) <= max_lines:
        return text
    result = []
    i = 0
    budget = max_lines
    section_lines_kept = 0
    section_line_limit = 30
    while i < len(lines) and budget > 0:
        line = lines[i]
        stripped = line.strip()
        is_heading = (
            re.match(r'^#{1,6}\s', stripped) or
            re.match(r'^\d+(\.\d+)*\s+[A-Z]', stripped) or
            re.match(r'^(Chapter|Appendix|Part|Section)\s+\d', stripped, re.IGNORECASE) or
            (stripped.isupper() and 3 < len(stripped) < 80)
        )
        if is_heading:
            result.append(line)
            budget -= 1
            section_lines_kept = 0
        elif not stripped:
            result.append(line)
            budget -= 1
        elif section_lines_kept < section_line_limit:
            result.append(line)
            budget -= 1
            section_lines_kept += 1
        elif section_lines_kept == section_line_limit:
            result.append('... [content trimmed for brevity] ...')
            budget -= 1
            section_lines_kept += 1
        i += 1
    if i < len(lines):
        result.append(f'\n... [{len(lines) - i} lines omitted] ...')
    return '\n'.join(result)


def extract_single_pdf(pdf_path: Path) -> tuple:
    product, version, doc_name = classify_pdf_path(pdf_path)
    title = title_from_filename(pdf_path)
    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
    except Exception:
        return product, version, doc_name, None
    text_by_page = []
    for page in reader.pages:
        try:
            text_by_page.append(page.extract_text() or '')
        except Exception:
            text_by_page.append('')
    full_text = '\n'.join(text_by_page)
    if not full_text.strip():
        return product, version, doc_name, None
    headings = detect_headings(full_text)
    seen = set()
    unique_headings = []
    for h in headings:
        normalized = h.strip()
        if normalized not in seen:
            seen.add(normalized)
            unique_headings.append(normalized)
    table_pages = find_table_pages(text_by_page)
    tables_md = []
    if table_pages:
        tables_md = extract_tables_pdfplumber(pdf_path, table_pages[:50])
    md_parts = []
    md_parts.append(f'# {title}')
    md_parts.append('')
    md_parts.append(f'**Source:** `{pdf_path.name}`  ')
    md_parts.append(f'**Pages:** {num_pages}  ')
    md_parts.append(f'**Product:** {product} | **Version:** {version}')
    md_parts.append('')
    if unique_headings:
        md_parts.append('## Table of Contents')
        md_parts.append('')
        for h in unique_headings[:100]:
            depth = len(re.findall(r'\.', h.split()[0])) if re.match(r'^\d', h) else 0
            indent = '  ' * min(depth, 3)
            md_parts.append(f'{indent}- {h}')
        md_parts.append('')
    md_parts.append('## Content')
    md_parts.append('')
    content_lines = []
    for line in full_text.split('\n'):
        stripped = line.strip()
        if not stripped:
            content_lines.append('')
            continue
        if re.match(r'^\d+(\.\d+)*\s+[A-Z]', stripped):
            dots = stripped.split()[0].count('.')
            level = min(dots + 2, 6)
            content_lines.append(f'{"#" * level} {stripped}')
        elif re.match(r'^(Chapter|Appendix|Part)\s+\d', stripped, re.IGNORECASE):
            content_lines.append(f'## {stripped}')
        else:
            content_lines.append(stripped)
    content_text = '\n'.join(content_lines)
    content_text = summarize_dense_text(content_text, MAX_OUTPUT_LINES - len(md_parts))
    md_parts.append(content_text)
    if tables_md:
        md_parts.append('')
        md_parts.append('## Extracted Tables')
        md_parts.append('')
        for i, table in enumerate(tables_md[:30], 1):
            md_parts.append(f'### Table {i}')
            md_parts.append('')
            md_parts.append(table)
            md_parts.append('')
    markdown = '\n'.join(md_parts)
    return product, version, doc_name, markdown


def process_pdf_task(pdf_path_str: str) -> dict:
    pdf_path = Path(pdf_path_str)
    try:
        product, version, doc_name, markdown = extract_single_pdf(pdf_path)
        if markdown is None:
            return {
                'success': False,
                'pdf': pdf_path_str,
                'error': 'No text extracted (possibly scanned/image PDF)',
                'product': product,
                'version': version,
                'doc_name': doc_name,
            }
        return {
            'success': True,
            'pdf': pdf_path_str,
            'product': product,
            'version': version,
            'doc_name': doc_name,
            'markdown': markdown,
            'lines': markdown.count('\n'),
        }
    except Exception as e:
        product, version, doc_name = classify_pdf_path(pdf_path)
        return {
            'success': False,
            'pdf': pdf_path_str,
            'error': f'{type(e).__name__}: {e}',
            'product': product,
            'version': version,
            'doc_name': doc_name,
        }


def process_large_reference_pdf(pdf_path: Path) -> list:
    results = []
    title = "OpenAM 12 Reference"
    product, version = "openam", "12"
    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)
        print(f"  [reference] Loaded {num_pages} pages")
    except Exception as e:
        results.append({
            'success': False,
            'pdf': str(pdf_path),
            'error': f'Failed to open: {e}',
            'product': product,
            'version': version,
            'doc_name': pdf_path.stem,
        })
        return results
    text_by_page = []
    for i, page in enumerate(reader.pages):
        try:
            text_by_page.append(page.extract_text() or '')
        except Exception:
            text_by_page.append('')
        if (i + 1) % 100 == 0:
            print(f"  [reference] Extracted text from {i+1}/{num_pages} pages")
    print(f"  [reference] Text extraction complete")
    sections = []
    for i, text in enumerate(text_by_page):
        for line in text.split('\n')[:5]:
            stripped = line.strip()
            m = re.match(
                r'^(Chapter|Appendix|Part)\s+(\d+|[A-Z])\b[.:]?\s*(.*)',
                stripped,
                re.IGNORECASE,
            )
            if m:
                kind = m.group(1).title()
                num = m.group(2)
                rest = m.group(3).strip().rstrip('.')
                sec_title = f'{kind} {num}'
                if rest:
                    sec_title += f' - {rest}'
                sections.append({'title': sec_title, 'start_page': i})
                break
    if not sections:
        chunk_size = 50
        for start in range(0, num_pages, chunk_size):
            end = min(start + chunk_size, num_pages)
            sections.append({
                'title': f'Pages {start+1}-{end}',
                'start_page': start,
            })
    print(f"  [reference] Found {len(sections)} sections")
    page_ranges = []
    for i, sec in enumerate(sections):
        start = sec['start_page']
        end = sections[i + 1]['start_page'] if i + 1 < len(sections) else num_pages
        page_ranges.append((sec['title'], start, end))
    for sec_title, start, end in page_ranges:
        section_text_parts = [text_by_page[p] for p in range(start, end)]
        section_text = '\n'.join(section_text_parts)
        if not section_text.strip():
            continue
        headings = detect_headings(section_text)
        seen = set()
        unique_headings = []
        for h in headings:
            if h.strip() not in seen:
                seen.add(h.strip())
                unique_headings.append(h.strip())
        table_pages_rel = find_table_pages(section_text_parts)
        table_pages_abs = [start + p for p in table_pages_rel]
        tables_md = []
        if table_pages_abs:
            tables_md = extract_tables_pdfplumber(pdf_path, table_pages_abs[:30])
        doc_name = sanitize_filename(sec_title.lower().replace(' ', '-'))
        md_parts = []
        md_parts.append(f'# {title} - {sec_title}')
        md_parts.append('')
        md_parts.append(f'**Source:** `{pdf_path.name}`  ')
        md_parts.append(f'**Pages:** {start+1}-{end} of {num_pages}  ')
        md_parts.append(f'**Product:** {product} | **Version:** {version}')
        md_parts.append('')
        if unique_headings:
            md_parts.append('## Section Contents')
            md_parts.append('')
            for h in unique_headings[:60]:
                depth = len(re.findall(r'\.', h.split()[0])) if re.match(r'^\d', h) else 0
                indent = '  ' * min(depth, 3)
                md_parts.append(f'{indent}- {h}')
            md_parts.append('')
        md_parts.append('## Content')
        md_parts.append('')
        content_lines = []
        for line in section_text.split('\n'):
            stripped = line.strip()
            if not stripped:
                content_lines.append('')
                continue
            if re.match(r'^\d+(\.\d+)*\s+[A-Z]', stripped):
                dots = stripped.split()[0].count('.')
                level = min(dots + 2, 6)
                content_lines.append(f'{"#" * level} {stripped}')
            elif re.match(r'^(Chapter|Appendix|Part)\s+\d', stripped, re.IGNORECASE):
                content_lines.append(f'## {stripped}')
            else:
                content_lines.append(stripped)
        content_text = '\n'.join(content_lines)
        content_text = summarize_dense_text(content_text, MAX_OUTPUT_LINES - len(md_parts))
        md_parts.append(content_text)
        if tables_md:
            md_parts.append('')
            md_parts.append('## Extracted Tables')
            md_parts.append('')
            for ti, table in enumerate(tables_md[:20], 1):
                md_parts.append(f'### Table {ti}')
                md_parts.append('')
                md_parts.append(table)
                md_parts.append('')
        markdown = '\n'.join(md_parts)
        results.append({
            'success': True,
            'pdf': str(pdf_path),
            'product': product,
            'version': version,
            'doc_name': doc_name,
            'markdown': markdown,
            'lines': markdown.count('\n'),
            'section': sec_title,
        })
    return results


def write_result(result: dict):
    if not result['success']:
        return None
    out_dir = OUTPUT / result['product'] / result['version']
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{result['doc_name']}.md"
    out_file.write_text(result['markdown'], encoding='utf-8')
    return out_file


def main():
    start_time = time.time()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    errors = []
    success_count = 0
    total_lines = 0
    archive_pdfs = sorted(ARCHIVE.rglob('*.pdf'))
    print(f"Found {len(archive_pdfs)} PDFs in archive")
    print(f"\n{'='*60}")
    print(f"Processing OpenAM-12-Reference.pdf ({REFERENCE})")
    print(f"{'='*60}")
    if REFERENCE.exists():
        ref_results = process_large_reference_pdf(REFERENCE)
        for r in ref_results:
            if r['success']:
                out_path = write_result(r)
                success_count += 1
                total_lines += r['lines']
                section = r.get('section', '')
                print(f"  [OK] {section} -> {out_path} ({r['lines']} lines)")
            else:
                errors.append(r)
                print(f"  [FAIL] {r.get('section', r['doc_name'])}: {r['error']}")
    else:
        print(f"  [SKIP] File not found: {REFERENCE}")
    print(f"\n{'='*60}")
    print(f"Processing {len(archive_pdfs)} archive PDFs (parallel, {MAX_WORKERS} workers)")
    print(f"{'='*60}")
    pdf_paths_str = [str(p) for p in archive_pdfs]
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_pdf = {
            executor.submit(process_pdf_task, p): p for p in pdf_paths_str
        }
        completed = 0
        for future in as_completed(future_to_pdf):
            completed += 1
            result = future.result()
            if result['success']:
                out_path = write_result(result)
                success_count += 1
                total_lines += result['lines']
                if completed % 50 == 0 or completed == len(pdf_paths_str):
                    print(f"  Progress: {completed}/{len(pdf_paths_str)} processed, {success_count} OK")
            else:
                errors.append(result)
                if completed <= 5 or completed % 50 == 0:
                    print(f"  [FAIL] {result['pdf']}: {result['error']}")
    if errors:
        error_lines = [
            '# PDF Extraction Errors',
            '',
            f'**Total errors:** {len(errors)}  ',
            f'**Date:** {time.strftime("%Y-%m-%d %H:%M:%S")}',
            '',
            '| PDF | Error |',
            '| --- | --- |',
        ]
        for err in errors:
            pdf_name = Path(err['pdf']).name
            error_msg = err.get('error', 'Unknown error').replace('|', '\\|')
            error_lines.append(f'| `{pdf_name}` | {error_msg} |')
        ERROR_LOG.write_text('\n'.join(error_lines), encoding='utf-8')
        print(f"\nError log written to: {ERROR_LOG}")
    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"  Files extracted:  {success_count}")
    print(f"  Total lines:      {total_lines}")
    print(f"  Errors:           {len(errors)}")
    print(f"  Time elapsed:     {elapsed:.1f}s")
    print(f"  Output directory:  {OUTPUT}")


if __name__ == '__main__':
    main()
