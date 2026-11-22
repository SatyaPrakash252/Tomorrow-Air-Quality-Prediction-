"""
scientific_formatter.py
───────────────────────
High-precision typography engine for converting scientific, chemical, 
and mathematical expressions into richly formatted python-docx runs.

Handles:
1. Chemical Species: PM_{2.5}, PM2.5, PM10, NO2, SO2, CO2, O3, NOx, NH3
2. Scientific Units: μg/m^3, μg/m3, ug/m3, mg/m3, m^2/s, °C
3. Mathematical & Statistical: R^2, R², p-value, t-test, p < 0.05, 10^-5,
   Vg, HRI_g, w_p, C_p, β_p, P_25, P_75, P_90, t+1, t-1, etc.
4. Inline LaTeX math: $...$
5. Markdown syntax: **bold**, *italic*
"""

import re
from docx.shared import Pt, RGBColor


def add_formatted_runs(paragraph, text, base_font_size=12, base_bold=False, base_italic=False, 
                       base_font_name='Times New Roman', font_color=None):
    """
    Parses `text` and adds correctly formatted runs to `paragraph`.
    Supports chemical subscripts, unit superscripts, statistical formatting,
    inline LaTeX math ($...$), and markdown bold/italic.
    """
    if not text:
        return []

    # First, split text by markdown bold `**...**` and math `$ ... $`
    # We will build a unified tokenizer
    tokens = _tokenize_text(text)
    
    runs = []
    for token in tokens:
        r = paragraph.add_run(token['text'])
        r.font.name = token.get('font_name', base_font_name)
        fsize = token.get('font_size', base_font_size)
        if token.get('subscript') or token.get('superscript'):
            fsize = round(fsize * 0.75, 1)
        r.font.size = Pt(fsize)
        r.bold = token.get('bold', base_bold)
        r.italic = token.get('italic', base_italic)
        r.font.subscript = token.get('subscript', False)
        r.font.superscript = token.get('superscript', False)
        if font_color:
            r.font.color.rgb = font_color
        runs.append(r)
        
    return runs


def format_cell_text(cell, text, base_font_size=9, base_bold=False, base_italic=False, 
                     base_font_name='Times New Roman', alignment=None):
    """Formats text within a table cell using scientific typography."""
    cell.text = ""  # Clear default run
    p = cell.paragraphs[0]
    if alignment is not None:
        p.alignment = alignment
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    return add_formatted_runs(p, text, base_font_size=base_font_size, 
                              base_bold=base_bold, base_italic=base_italic, 
                              base_font_name=base_font_name)


def _tokenize_text(text):
    """
    Tokenizes raw text into a list of dicts with styling properties:
    {'text': str, 'bold': bool, 'italic': bool, 'subscript': bool, 'superscript': bool, ...}
    """
    # Step 1: Pre-process special Unicode characters to normalized forms
    text = text.replace('₂.₅', '2.5').replace('₁₀', '10').replace('₂', '2').replace('₃', '3')
    # Superscript digits
    for sup_char, num in [('⁰', '0'), ('¹', '1'), ('²', '2'), ('³', '3'), ('⁴', '4'),
                          ('⁵', '5'), ('⁶', '6'), ('⁷', '7'), ('⁸', '8'), ('⁹', '9')]:
        text = text.replace(sup_char, f'^{num}')
    text = re.sub(r'\^(\d+)\^(\d+)', r'^\1\2', text)
    text = text.replace('⁻⁵', '^-5').replace('⁻⁶', '^-6').replace('⁻⁴', '^-4').replace('⁻³', '^-3').replace('⁻²', '^-2').replace('⁻¹', '^-1')
    text = text.replace('µ', 'μ')

    # Step 2: Master regex pattern for scientific and mathematical terms
    pattern = re.compile(
        r'(\$[^\$]+\$)'                                      # 1: Inline math
        r'|(\*\*[^\*]+\*\*)'                                 # 2: Bold
        r'|((?<![\w*])\*[a-zA-Z0-9_\-]+\*(?![\w*]))'        # 3: True markdown italic (not multiplication '*')
        r'|(\bPM\s*[_]?(?:2\.5|10|1)\b)'                    # 4: PM2.5, PM10, PM 2.5
        r'|(\b(?:NO|SO|CO)[_]?2\b)'                          # 5: NO2, SO2, CO2
        r'|(\bO[_]?3\b)'                                     # 6: O3
        r'|(\bNO[_]?x\b)'                                    # 7: NOx
        r'|(\bNH[_]?3\b)'                                    # 8: NH3
        r'|(\bC6H6\b)'                                       # 8b: C6H6 benzene
        r'|([μu]g\/m\^?3)'                                   # 9: ug/m3
        r'|(\bmg\/m\^?3\b)'                                  # 10: mg/m3
        r'|(\bm\^?2\/s\b)'                                   # 11: m2/s
        r'|(\bR\^2\b)'                                       # 12: R^2
        r'|(\bR_val\^2\b)'                                   # 13: R_val^2
        r'|(\b[pt]\s*[-–]\s*value\b)'                        # 14: p-value
        r'|(\bt\s*[-–]\s*test\b)'                            # 15: t-test
        r'|(\b[ptWwFZz]\s*[<>=≤≥]\s*[-−]?\d*\.?\d+(?:[eE][-−]?\d+)?\b)' # 16: p < 0.05 / t = -3.722 / W = 1263583
        r'|(\b(?:HRI|V|w|C|P|S|I|B|y|x)[_]?(?:[gpdmij]|GP|hi|lo|25|75|90|0)\b)' # 17: V_g, w_p, C_p, S_p, I_p, B_hi, B_lo, w_0, w_m, y_i
        r'|(\b10\^[-−]?\d+\b)'                               # 18: 10^-5
        r'|([βγ][\s_]?[pgd])'                                # 19: β_p, β_g, γ_p
        r'|([fg][\s_]?[θϕ])'                                 # 19b: f_θ, g_ϕ
        r'|([Zz][\s_]?(?:MMA|MICE|KNN|SVD)\b)'               # 19c: Z_MMA, z_KNN, z_MICE, z_SVD
        r'|([yŷ]\s*[\^_]?[mi]\b)'                            # 19d: ŷ_m, ŷ_i
        r'|(ℝ\^?\d+)'                                        # 19e: ℝ^36, ℝ³⁶
        r'|(\b[t][\+\-][123]\b)'                             # 20: t+1, t-1
    )

    result_tokens = []
    last_end = 0

    for match in pattern.finditer(text):
        start, end = match.span()
        if start > last_end:
            result_tokens.append({'text': text[last_end:start]})
        
        m_str = match.group()
        
        # 1. Inline math $ ... $
        if m_str.startswith('$') and m_str.endswith('$'):
            math_content = m_str[1:-1].strip()
            result_tokens.extend(_parse_inline_math(math_content))
            
        # 2. Markdown Bold **...**
        elif m_str.startswith('**') and m_str.endswith('**'):
            inner = m_str[2:-2]
            inner_tokens = _tokenize_text(inner)
            for t in inner_tokens:
                t['bold'] = True
            result_tokens.extend(inner_tokens)

        # 3. Markdown Italic *...*
        elif m_str.startswith('*') and m_str.endswith('*'):
            inner = m_str[1:-1]
            inner_tokens = _tokenize_text(inner)
            for t in inner_tokens:
                t['italic'] = True
            result_tokens.extend(inner_tokens)

        # 4. PM2.5, PM10, PM1, PM 2.5
        elif 'PM' in m_str:
            num = m_str.replace('PM', '').replace('_', '').strip()
            result_tokens.append({'text': 'PM'})
            result_tokens.append({'text': num, 'subscript': True})

        # 5. NO2, SO2, CO2
        elif any(gas in m_str for gas in ['NO2', 'SO2', 'CO2', 'NO_2', 'SO_2', 'CO_2']):
            gas_name = m_str[:2]
            result_tokens.append({'text': gas_name})
            result_tokens.append({'text': '2', 'subscript': True})

        # 6. O3
        elif 'O' in m_str and '3' in m_str:
            result_tokens.append({'text': 'O'})
            result_tokens.append({'text': '3', 'subscript': True})

        # 7. NOx
        elif 'NO' in m_str and 'x' in m_str:
            result_tokens.append({'text': 'NO'})
            result_tokens.append({'text': 'x', 'subscript': True})

        # 8. NH3
        elif 'NH' in m_str and '3' in m_str:
            result_tokens.append({'text': 'NH'})
            result_tokens.append({'text': '3', 'subscript': True})

        # 8b. C6H6 benzene
        elif m_str == 'C6H6':
            result_tokens.append({'text': 'C'})
            result_tokens.append({'text': '6', 'subscript': True})
            result_tokens.append({'text': 'H'})
            result_tokens.append({'text': '6', 'subscript': True})

        # 9. μg/m3, ug/m3
        elif 'g/m' in m_str:
            prefix = 'μg/m' if ('μ' in m_str or 'µ' in m_str or 'u' in m_str) else 'mg/m'
            result_tokens.append({'text': prefix})
            result_tokens.append({'text': '3', 'superscript': True})

        # 11. m2/s
        elif 'm' in m_str and '/s' in m_str:
            result_tokens.append({'text': 'm'})
            result_tokens.append({'text': '2', 'superscript': True})
            result_tokens.append({'text': '/s'})

        # 12. R^2
        elif m_str == 'R^2':
            result_tokens.append({'text': 'R', 'italic': True})
            result_tokens.append({'text': '2', 'superscript': True})

        # 13. R_val^2
        elif m_str == 'R_val^2':
            result_tokens.append({'text': 'R', 'italic': True})
            result_tokens.append({'text': 'val', 'subscript': True})
            result_tokens.append({'text': '2', 'superscript': True})

        # 14. p-value
        elif 'value' in m_str and ('p' in m_str or 't' in m_str):
            char = 'p' if 'p' in m_str else 't'
            sep = '-value'
            result_tokens.append({'text': char, 'italic': True})
            result_tokens.append({'text': sep})

        # 15. t-test
        elif 'test' in m_str and 't' in m_str:
            result_tokens.append({'text': 't', 'italic': True})
            result_tokens.append({'text': '-test'})

        # 16. p < 0.05, t = -3.722, W = 1263583
        elif any(op in m_str for op in ['<', '>', '=', '≤', '≥']) and m_str[0] in 'ptWwFZz':
            stat_char = m_str[0]
            rest = m_str[1:]
            result_tokens.append({'text': stat_char, 'italic': True})
            result_tokens.append({'text': rest})

        # 17. Variable subscripts: V_g, w_p, C_p, S_p, I_p, B_hi, B_lo, I_hi, I_lo, y_i, etc.
        elif any(m_str.startswith(v) for v in ['V', 'w', 'C', 'P', 'S', 'HRI', 'I', 'B', 'y', 'x']):
            if m_str.startswith('HRI'):
                var = 'HRI'
                sub = m_str[3:].replace('_', '')
                result_tokens.append({'text': var})
                result_tokens.append({'text': sub, 'subscript': True})
            else:
                var = m_str[0]
                sub = m_str[1:].replace('_', '')
                result_tokens.append({'text': var, 'italic': True})
                result_tokens.append({'text': sub, 'subscript': True})

        # 18. 10^-5
        elif m_str.startswith('10^'):
            exp = m_str[3:]
            result_tokens.append({'text': '10'})
            result_tokens.append({'text': exp, 'superscript': True})

        # 19. β_p, β_g, γ_p
        elif any(g in m_str for g in ['β', 'γ']):
            g_char = m_str[0]
            sub = m_str[1:].replace('_', '').strip()
            result_tokens.append({'text': g_char, 'italic': True})
            result_tokens.append({'text': sub, 'subscript': True})

        # 19b. f_θ, g_ϕ
        elif any(f in m_str for f in ['f', 'g']) and any(greek in m_str for greek in ['θ', 'ϕ']):
            var = m_str[0]
            sub = m_str[1:].replace('_', '').strip()
            result_tokens.append({'text': var, 'italic': True})
            result_tokens.append({'text': sub, 'subscript': True})

        # 19c. Z_MMA, z_KNN, z_MICE, z_SVD
        elif any(z in m_str for z in ['Z', 'z']) and any(tag in m_str for tag in ['MMA', 'MICE', 'KNN', 'SVD']):
            var = m_str[0]
            sub = m_str[1:].replace('_', '').strip()
            result_tokens.append({'text': var, 'italic': True})
            result_tokens.append({'text': sub, 'subscript': True})

        # 19d. ŷ_m, ŷ_i
        elif any(y in m_str for y in ['y', 'ŷ', 'ŷ']) and any(sub_idx in m_str for sub_idx in ['m', 'i']):
            var = 'ŷ'
            sub = 'm' if 'm' in m_str else 'i'
            result_tokens.append({'text': var, 'italic': True})
            result_tokens.append({'text': sub, 'subscript': True})

        # 19e. ℝ^d
        elif 'ℝ' in m_str:
            exp = m_str.replace('ℝ', '').replace('^', '').strip()
            result_tokens.append({'text': 'ℝ'})
            if exp:
                result_tokens.append({'text': exp, 'superscript': True})

        # 20. t+1, t-1
        elif m_str.startswith('t') and ('+' in m_str or '-' in m_str):
            result_tokens.append({'text': 't', 'italic': True})
            result_tokens.append({'text': m_str[1:]})

        else:
            result_tokens.append({'text': m_str})

        last_end = end

    if last_end < len(text):
        result_tokens.append({'text': text[last_end:]})

    return result_tokens


def _parse_inline_math(math_str):
    """Parses clean inline LaTeX math like R^2, t = -3.722, p < 0.0001, \\beta_p into tokens."""
    math_tokens = []
    
    # Common mathematical conversions
    math_str = math_str.replace('\\text{PM}_{2.5}', 'PM2.5')
    math_str = math_str.replace('\\text{PM}_{10}', 'PM10')
    math_str = math_str.replace('\\text{NO}_2', 'NO2')
    math_str = math_str.replace('\\text{SO}_2', 'SO2')
    math_str = math_str.replace('\\text{CO}', 'CO')
    math_str = math_str.replace('\\text{O}_3', 'O3')
    math_str = math_str.replace('\\mu g/m^3', 'μg/m3')
    math_str = math_str.replace('\\mu\\text{g/m}^3', 'μg/m3')
    math_str = math_str.replace('\\bar{d}', 'd_mean')
    math_str = math_str.replace('\\times', '×')
    math_str = math_str.replace('\\le', '≤').replace('\\ge', '≥')
    math_str = math_str.replace('\\beta', 'β').replace('\\gamma', 'γ').replace('\\tau', 'τ').replace('\\theta', 'θ')

    # Now run general tokenizer over cleaned math string
    cleaned_tokens = _tokenize_text(math_str)
    for t in cleaned_tokens:
        # Single-letter variable names inside math should be italicized
        txt = t['text'].strip()
        if len(txt) == 1 and txt.isalpha() and not t.get('subscript') and not t.get('superscript'):
            t['italic'] = True
        math_tokens.append(t)
        
    return math_tokens
