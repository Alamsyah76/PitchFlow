"""
Email Builder — build HTML email body
======================================
Single responsibility: generate the HTML email from a contact dict.
Now supports fully customisable sections: header, greeting, intro, closing, signature, footer.
"""
import base64
from pathlib import Path
from modules.config import PROJECT_ROOT


def _default_body(contact):
    """Konten default jika tidak ada template yang dipilih — kosong."""
    return ""


# ── Default Sections ────────────────────────────────────────────────

def _default_greeting(clean_name, company):
    return f"""<p class="greeting">Kepada Yth. Bapak/Ibu <strong>{clean_name}</strong>{f',<br>{company}' if company else ''}</p>"""


DEFAULT_HEADER = """<div class="header">
    <img src="data:image/png;base64,{logo_b64}" alt="Logo" class="logo-img">
</div>"""

DEFAULT_INTRO = """<div class="intro">
    <strong>Perkenalkan, Saya <span style="color: #0056b3;">{sender}</span> dari <span style="color: #0056b3;">{sender_company}</span>.</strong>
</div>"""

DEFAULT_CLOSING = """"""

DEFAULT_SIGNATURE = """"""

DEFAULT_FOOTER = """"""


# ── Main Builder ────────────────────────────────────────────────────

def build_email_body(
    contact,
    template_body=None,
    sender_name="",
    sender_email="",
    logo_b64="",
    sender_company="",
    # Fully customisable sections — fallback to defaults above
    template_header=None,
    template_greeting=None,
    template_intro=None,
    template_closing=None,
    template_signature=None,
    template_footer=None,
):
    """
    Build complete HTML email from contact data and optional per-section templates.
    Support placeholders in ALL sections: {name}, {company}, {email}, {job_title},
    {phone}, {sender}, {sender_company}, {sender_email_addr}
    """
    name = contact["name"]
    company = contact.get("company", "")
    email = contact.get("email", "")
    job_title = contact.get("job_title", "")
    phone = contact.get("phone", "")
    clean_name = name.split(",")[0].strip().title()

    # Sender info
    sender = sender_name or ""
    sc = sender_company or ""
    se = sender_email or ""

    # Helper: replace placeholders in any HTML snippet
    def _fill(text):
        if not text:
            return ""
        t = text.replace("{name}", clean_name)
        t = t.replace("{company}", company)
        t = t.replace("{email}", email)
        t = t.replace("{job_title}", job_title)
        t = t.replace("{phone}", phone)
        t = t.replace("{sender}", sender)
        t = t.replace("{sender_company}", sc)
        t = t.replace("{sender_email_addr}", se)
        return t

    # Body content
    body_content = template_body if template_body else _default_body(contact)
    body_content = _fill(body_content)

    # Logo
    if not logo_b64:
        logo_path = PROJECT_ROOT / "frontend" / "public" / "pitchflow.png"
        if logo_path.exists():
            logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()

    # Sections — each falls back to its default if not provided
    if template_header is not None:
        header_html = _fill(template_header)
        # If header is empty but we have a logo, show default header with logo
        if not header_html and logo_b64:
            header_html = DEFAULT_HEADER.format(logo_b64=logo_b64)
    else:
        header_html = DEFAULT_HEADER.format(logo_b64=logo_b64)
    greeting_html = _fill(template_greeting) if template_greeting is not None else _default_greeting(clean_name, company)
    intro_html    = _fill(template_intro)    if template_intro is not None    else _fill(DEFAULT_INTRO)
    closing_html  = _fill(template_closing)  if template_closing is not None  else _fill(DEFAULT_CLOSING)
    signature_html= _fill(template_signature) if template_signature is not None else _fill(DEFAULT_SIGNATURE)
    footer_html   = _fill(template_footer)   if template_footer is not None   else _fill(DEFAULT_FOOTER)

    html = f"""\
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', Arial, Helvetica, sans-serif; line-height: 1.7; color: #333; margin: 0; padding: 0; background-color: #f5f7fa; }}
        .container {{ max-width: 620px; margin: 20px auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
        .header {{ background: #ffffff; padding: 28px 30px 8px; text-align: center; border-bottom: 1px solid #e8e8e8; }}
        .header .logo-img {{ max-width: 260px; height: auto; margin-bottom: 6px; }}
        .content {{ padding: 28px 30px; }}
        .content p {{ margin: 0 0 14px; }}
        .greeting {{ font-size: 16px; margin-bottom: 18px; }}
        .intro {{ background-color: #eef4fb; padding: 16px 20px; border-left: 4px solid #0056b3; margin: 18px 0; border-radius: 0 6px 6px 0; font-size: 15px; }}
        .content .segment {{ margin: 22px 0; padding: 18px 20px; border: 1px solid #e0e7ef; border-radius: 8px; }}
        .content .segment h3 {{ margin: 0 0 10px; font-size: 16px; color: #0056b3; }}
        .content .segment ul {{ margin: 8px 0 0; padding-left: 20px; }}
        .content .segment ul li {{ margin-bottom: 6px; font-size: 14px; }}
        .badge {{ display: inline-block; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 12px; margin-right: 6px; }}
        .badge-enduser {{ background: #e8f5e9; color: #2e7d32; }}
        .badge-partner {{ background: #fff3e0; color: #e65100; }}
        .highlight-box {{ background-color: #f8faff; padding: 14px 18px; border-radius: 6px; margin: 14px 0; font-size: 14px; border: 1px dashed #b3cceb; }}
        .footer {{ padding: 20px 30px; font-size: 12px; color: #888; border-top: 1px solid #e8e8e8; background: #fafafa; }}
        .footer a {{ color: #0056b3; text-decoration: none; }}
        .divider {{ border: none; border-top: 1px solid #e8e8e8; margin: 16px 0; }}
        @media only screen and (max-width: 640px) {{ .container {{ margin: 10px; }} .content, .header, .footer {{ padding-left: 18px; padding-right: 18px; }} }}
    </style>
</head>
<body>
    <div class="container">
        {header_html}
        <div class="content">
            {greeting_html}

            {intro_html}

            {body_content}

            {closing_html}

            {signature_html}
        </div>
        <div class="footer">
            {footer_html}
        </div>
    </div>
</body>
</html>"""
    return html
