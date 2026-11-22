import markdown

def generate_html():
    with open('final_submission/PROJECT_COMPREHENSIVE_TECHNICAL_MANUAL.md', 'r', encoding='utf-8') as f:
        text = f.read()

    # Convert markdown to HTML body
    html_body = markdown.markdown(text, extensions=['tables', 'fenced_code'])

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VayuDrishti - Complete Technical Architecture & Defense Manual</title>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        :root {{
            --primary: #0284c7;
            --primary-dark: #0369a1;
            --bg: #f8fafc;
            --surface: #ffffff;
            --text: #0f172a;
            --muted: #64748b;
            --border: #e2e8f0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.68;
            color: var(--text);
            background: var(--bg);
            margin: 0;
            padding: 2.5rem 1rem;
        }}
        .container {{
            max-width: 960px;
            margin: 0 auto;
            background: var(--surface);
            padding: 3.5rem 4rem;
            border-radius: 16px;
            box-shadow: 0 4px 25px rgba(0, 0, 0, 0.06);
            border: 1px solid var(--border);
        }}
        h1, h2, h3, h4 {{
            color: #0f172a;
            font-weight: 600;
            letter-spacing: -0.02em;
        }}
        h1 {{ font-size: 2.25rem; border-bottom: 2px solid var(--border); padding-bottom: 0.75rem; margin-top: 0; }}
        h2 {{ font-size: 1.5rem; margin-top: 2.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; color: var(--primary-dark); }}
        h3 {{ font-size: 1.2rem; margin-top: 1.75rem; }}
        blockquote {{
            border-left: 4px solid var(--primary);
            margin: 1.5rem 0;
            padding: 0.85rem 1.25rem;
            background: #f0f9ff;
            color: #0369a1;
            border-radius: 0 8px 8px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            font-size: 0.92rem;
        }}
        th, td {{
            padding: 0.75rem 1rem;
            border: 1px solid var(--border);
            text-align: left;
        }}
        th {{
            background: #f1f5f9;
            font-weight: 600;
            color: #334155;
        }}
        tr:nth-child(even) {{ background: #f8fafc; }}
        code {{
            font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
            background: #f1f5f9;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.88em;
            color: #b91c1c;
        }}
        pre {{
            background: #0f172a;
            color: #f8fafc;
            padding: 1.25rem;
            border-radius: 8px;
            overflow-x: auto;
        }}
        pre code {{
            background: transparent;
            color: inherit;
            padding: 0;
        }}
        .print-btn {{
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 9999px;
            font-weight: 500;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4);
            transition: all 0.2s;
        }}
        .print-btn:hover {{ background: var(--primary-dark); transform: scale(1.05); }}
        @media print {{
            body {{ padding: 0; background: white; }}
            .container {{ box-shadow: none; border: none; padding: 0; max-width: 100%; }}
            .print-btn {{ display: none; }}
        }}
    </style>
</head>
<body>
    <button class="print-btn" onclick="window.print()">Print / Save to PDF</button>
    <div class="container">
        {html_body}
    </div>
</body>
</html>"""

    with open('final_submission/PROJECT_COMPREHENSIVE_TECHNICAL_MANUAL.html', 'w', encoding='utf-8') as f:
        f.write(full_html)

    with open('PROJECT_COMPREHENSIVE_TECHNICAL_MANUAL.html', 'w', encoding='utf-8') as f:
        f.write(full_html)

    print('HTML manual generated successfully.')

if __name__ == '__main__':
    generate_html()
