"""Builds products.html, the category pages and the product pages.

Run from the repository root:  python tools/build_products.py
Content lives in tools/products_data.py. The shared header and footer are
copied from about.html, so edit those there and re-run this script.
"""
import html
import json
import os
import re
import sys
import urllib.parse
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from products_data import CATEGORIES, PRODUCTS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://oxypackglobal.com"
WA = "919624449910"
OUT_DIR = "products"
CAT = {c["key"]: c for c in CATEGORIES}
CAT_LABEL = {"corrugated": "Corrugated", "bags": "Paper bags", "cartons": "Cartons & boxes",
             "food": "Food service", "protective": "Protective"}
SELECT_OPTS = ["Corrugated boxes & cartons", "Paper bags & sacks", "Printed cartons & gift boxes",
               "Food service packaging", "Paper protective packaging", "Not sure yet"]
CAT_INDEX = {c["key"]: i for i, c in enumerate(CATEGORIES)}
for i, p in enumerate(PRODUCTS, 1):
    p["num"] = f"{i:02d}"
    p["img"] = f"assets/img/products/{p['num']}-{p['slug']}.jpg"

e = lambda s: html.escape(s, quote=True)
ARROW = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
         'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>')
DOWN = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M6 13l6 6 6-6"/></svg>')
WA_ICON = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a9 9 0 01-13.5 7.8L3 21l1.2-4.5A9 9 0 1121 12z"/></svg>')
TICK = ('<span class="tick"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#2E8424" stroke-width="3" '
        'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10"/></svg></span>')
BOX = ('<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2E8424" stroke-width="2" stroke-linecap="round" '
       'stroke-linejoin="round" aria-hidden="true"><path d="M3 7l9-4 9 4-9 4-9-4z"/><path d="M3 7v10l9 4 9-4V7"/><path d="M12 11v10"/></svg>')


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# ---------- shared chunks taken from about.html ----------
ABOUT = read("about.html")
ORG_LD = re.search(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": \["Organization".*?</script>', ABOUT).group(0)
HEADER = ABOUT[ABOUT.index('<a class="skip"'):ABOUT.index('<main id="main">')]
HEADER_BASE = HEADER.replace(' aria-current="page"', '')


def header_for(active):
    return HEADER_BASE.replace(f'<a href="{active}">', f'<a href="{active}" aria-current="page">') if active else HEADER_BASE
FOOTER = ABOUT[ABOUT.index('<footer class="site-footer">'):ABOUT.index('<script src="assets/js/main.js"')]

FOOTER_PRODUCTS = ('<div><h2>Products</h2><ul><li><a href="products.html">All products</a></li>'
                   + "".join(f'<li><a href="{OUT_DIR}/{c["slug"]}.html">{e(c["name"])}</a></li>' for c in CATEGORIES)
                   + '</ul></div>')
FOOTER_RE = re.compile(r'<div><h2>Products</h2><ul>.*?</ul></div>', re.S)
FOOTER = FOOTER_RE.sub(lambda m: FOOTER_PRODUCTS, FOOTER)


def prefixed(text, prefix):
    if not prefix:
        return text
    return re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|/|data:)([^"]+)"', lambda m: f'{m[1]}="{prefix}{m[2]}"', text)


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'


def crumbs_ld(items):
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": SITE + "/" + u} for i, (n, u) in enumerate(items, 1)]})


def page(path, title, desc, main, lds, image="assets/img/og-image.jpg", band=True, extra="", active="products.html", og_type="website"):
    prefix = "../" * path.count("/")
    url = SITE + "/" + path
    img = SITE + "/" + image
    head = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0B1F44">
<meta name="author" content="OXY PACK GLOBAL">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="OXY PACK GLOBAL">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:locale" content="en_IN">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{img}">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800;900&amp;family=Inter:wght@400;500;600;700&amp;family=Lexend:wght@600&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
<script>document.documentElement.classList.add("js")</script>
{ORG_LD}
{chr(10).join(lds)}
{extra}</head>
<body>
'''
    band_html = ('<section class="band"><div class="wrap"><h2>Need something not listed? We\'ll engineer it in paper.</h2>'
                 f'<a href="contact.html" class="btn btn-dark">Send your requirement {ARROW}</a></div></section>') if band else ""
    body = header_for(active) + '\n<main id="main">\n' + main + '\n</main>\n' + band_html + FOOTER + '<script src="assets/js/main.js" defer></script>\n</body>\n</html>\n'
    write(path, prefixed(head, prefix) + prefixed(body, prefix))


def crumbs(items):
    lis = "".join(f'<li><a href="{u}">{e(n)}</a></li>' for n, u in items[:-1])
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{lis}<li aria-current="page">{e(items[-1][0])}</li></ol></nav>'


def pcard(p, link):
    hot = p["hot"]
    return (f'<li class="pcard{" hot" if hot else ""}">'
            + ('<span class="hot-tag">High demand</span>' if hot else '')
            + f'<img src="{p["img"]}" alt="{e(p["alt"])}" width="640" height="480" class="pcard-img" loading="lazy" decoding="async">'
            f'<div class="pcard-top"><span class="pcat">{e(CAT_LABEL[p["cat"]])}</span></div>'
            f'<h3>{e(p["name"])}</h3><p>{e(p["short"])}</p>'
            f'<a class="pcard-cta" href="{link}">View details{ARROW}<span class="sr-only"> of {e(p["name"])}</span></a></li>')


def quote_form(subject, cat_index=None, product=None):
    opts = "".join(f'<option{" selected" if i == cat_index else ""}>{e(o)}</option>' for i, o in enumerate(SELECT_OPTS))
    msg = e(f"Product: {product}\n") if product else ""
    hidden_product = f'<input type="hidden" name="product" value="{e(product)}">' if product else ""
    return f'''<div id="form-ok" class="form-msg" role="status" aria-live="polite">
<span class="ico-circle" style="width:76px;height:76px;margin:0 auto"><svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="#2E8424" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10"/></svg></span>
<h2 style="font-size:30px;margin:20px 0 8px">Thank you — enquiry received.</h2>
<p style="color:#4A566B">Our team will reply within one business day.</p>
<a href="https://wa.me/{WA}" target="_blank" rel="noopener" class="btn btn-wa" style="margin-top:24px">{WA_ICON} Need it sooner? WhatsApp us</a>
</div>
<form id="quote-form" action="https://formsubmit.co/sales@oxypackglobal.com" method="POST" data-endpoint="https://formsubmit.co/ajax/sales@oxypackglobal.com" style="display:flex;flex-direction:column;gap:20px">
<div><h2 style="font-size:28px;margin-bottom:6px">Get a free quote</h2><p style="font-size:15px;color:#4A566B">Takes under a minute. Fields marked * are required.</p></div>
<input type="hidden" name="_subject" value="{e(subject)}">
<input type="hidden" name="_template" value="table">
<input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
{hidden_product}
<div class="f2">
<div><label for="name">Full name *</label><input id="name" name="name" type="text" autocomplete="name" required></div>
<div><label for="email">Business email *</label><input id="email" name="email" type="email" autocomplete="email" required></div>
<div><label for="phone">Phone / WhatsApp</label><input id="phone" name="phone" type="tel" autocomplete="tel"></div>
<div><label for="country">Country</label><input id="country" name="country" type="text" autocomplete="country-name"></div>
<div><label for="category">Product category</label><select id="category" name="category">{opts}</select></div>
<div><label for="quantity">Estimated quantity</label><input id="quantity" name="quantity" type="text" placeholder="e.g. 10,000 pcs / month"></div>
</div>
<div><label for="message">Details</label><textarea id="message" name="message" rows="4" placeholder="Size, print, destination port — anything that helps us quote">{msg}</textarea></div>
<p id="form-err" class="form-err" role="alert">Sorry, something went wrong. Please email us at sales@oxypackglobal.com or WhatsApp +91 96244 49910.</p>
<div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap">
<button type="submit" class="btn btn-green">Get my free quote →</button>
<ul class="form-trust"><li>Reply within 1 business day</li><li>No obligation</li><li>Your details stay private</li></ul>
</div>
</form>'''


TRUST_ROW = ('<ul class="trust-row"><li>ISO 9001 certified</li><li>FSC® certified paper</li>'
             '<li>Exporting to 20+ countries</li><li>Reply within 1 business day</li></ul>')

# Customers shown in the "Trusted by" logo grid (home) and logo strip (other pages).
# file=None shows the name as a text tile. Logos live in assets/img/clients/.
CLIENTS = [
    ("Tiffany & Co.", "tiffany.svg", 634, 70), ("Logitech", "logitech.png", 236, 71),
    ("Zepto", "zepto.svg", 90, 30), ("UPL", "upl.svg", 1041, 462),
    ("Vadilal", "vadilal.svg", 150, 73), ("MDH", "mdh.png", 184, 60),
    ("Balaji Wafers", "balaji-wafers.svg", 140, 107), ("Chheda's", "chhedas.png", 296, 120),
    ("Mother's Recipe", "mothers-recipe.svg", 265, 100), ("GIVA", "giva.png", 411, 120),
    ("Gwalia Sweets", "gwalia-sweets.png", 124, 120), ("Vimal Healthy Oils", "vimal.png", 148, 120),
    ("Kitchen Xpress", "kitchen-xpress.png", 132, 120), ("Sheetal Ice Cream", "sheetal.png", 292, 120),
    ("Vijay Mamra", "vijay-mamra.png", 124, 99), ("Shubha", "shubha.png", 400, 84),
    ("Water2", "water2.png", 457, 113), ("Floky", "floky.png", 258, 62),
    ("BioRoot Labs", "bioroot.png", 382, 65), ("Nuvela Pharma", "nuvela-pharma.png", 155, 120),
    ("Alpha Crop Care", "alpha-crop-care.png", 120, 44), ("Primeseal Straps", "primeseal.png", 234, 114),
]


def client_item(name, f, w, h, hidden=False):
    alt = "" if hidden else e(name)
    if f:
        return f'<img src="assets/img/clients/{f}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async">'
    return f'<span class="client-name"{" aria-hidden=\"true\"" if hidden else ""}>{e(name)}</span>'


CLIENTS_GRID = ('<!-- clients -->\n<section class="sec clients" aria-labelledby="clients-h">\n<div class="wrap">\n'
                '<div class="sec-head reveal" style="justify-content:center;text-align:center"><div style="max-width:720px">'
                '<p class="eyebrow" style="justify-content:center">Our customers</p>'
                '<h2 class="h2" id="clients-h">Trusted by leading brands in India and abroad</h2>'
                '<p class="lead" style="margin-top:16px">From global names in jewellery and electronics to India&#8217;s best-known FMCG, food, agri and pharma companies.</p></div></div>\n'
                '<ul class="clients-grid">'
                + "".join(f'<li class="client">{client_item(*c)}</li>' for c in CLIENTS)
                + '<li class="client more"><span class="client-name">+ many more</span></li>'
                + '</ul>\n</div>\n</section>\n<!-- /clients -->')

_track = "".join(f'<li>{client_item(*c)}</li>' for c in CLIENTS)
_track_dup = "".join(f'<li aria-hidden="true">{client_item(*c, hidden=True)}</li>' for c in CLIENTS)
LOGO_STRIP = ('<!-- clients -->\n<section class="logo-strip" aria-label="Customers">\n'
              '<p class="logo-strip-label">Trusted by leading brands in India and abroad</p>\n'
              f'<div class="logo-viewport"><ul class="logo-track">{_track}{_track_dup}</ul></div>\n'
              '</section>\n<!-- /clients -->')
CLIENTS_RE = re.compile(r'<!-- clients -->.*?<!-- /clients -->\n?', re.S)

# Customer testimonials (approved in writing by each customer).
# "cats" = category pages the quote also appears on; "home" = shown on the home page.
TESTIMONIALS = [
    dict(company="Parle", role="Packaging & Purchase Department", industry="FMCG & consumer products", cats=["corrugated"], home=True,
         quote="Reliable packaging and consistency matter greatly in the FMCG industry. Oxy Pack Global has demonstrated a good understanding of packaging requirements, and we appreciate their focus on quality, product protection and professional coordination."),
    dict(company="Reliance Retail", role="Vendor Development Manager, Retail Operations", industry="Retail & distribution", cats=["bags"], home=True,
         quote="Efficient packaging and dependable supply coordination are essential to smooth business operations. We appreciate the professional approach of Oxy Pack Global and their focus on understanding packaging requirements and delivering appropriate solutions."),
    dict(company="Bikaji", role="Packaging Procurement Manager", industry="Namkeen & snacks", cats=["food"], home=True,
         quote="From packaging quality to product handling, every detail matters in the snacks industry. Oxy Pack Global has shown a good understanding of our packaging needs. We value their professionalism, communication and commitment towards delivering suitable solutions."),
    dict(company="Nuvela Pharma", role="Procurement Manager", industry="Pharmaceuticals", cats=["cartons"], home=True,
         quote="Packaging quality and consistency are very important in our industry. We appreciate Oxy Pack Global's professional approach, attention to specifications and responsiveness throughout the process. It has been a good experience working with their team."),
    dict(company="Shubha", role="Operations Manager", industry="Jewellery & lifestyle", cats=["cartons"], home=True,
         quote="Packaging is an important part of the overall customer experience for us. We appreciate the quality of work from Oxy Pack Global and their understanding of how packaging should complement a brand's presentation. Their team has been helpful and easy to coordinate with."),
    dict(company="Vijay Mamra", role="Purchase Manager", industry="Food & snacks", cats=[], home=True,
         quote="We were looking for packaging that offers durability and consistent quality for our products. Oxy Pack Global understood our requirements well and provided packaging solutions that suited our needs. Their coordination and commitment to quality have made our experience smooth."),
    dict(company="Primeseal Straps", role="Plant & Purchase Manager", industry="Industrial & manufacturing", cats=["corrugated", "protective"], home=False,
         quote="Finding a packaging supplier who understands industrial requirements makes a difference. Oxy Pack Global has been supportive with our packaging needs, and we appreciate their approach towards product protection, quality and timely coordination."),
    dict(company="Alpha Crop Care", role="Supply Chain Manager", industry="Agriculture & crop care", cats=["bags"], home=False,
         quote="We need packaging solutions that are practical, dependable and suitable for our operational requirements. Oxy Pack Global has been cooperative in understanding our needs and providing suitable packaging. We appreciate their service and professional communication."),
    dict(company="Gwalia Sweets", role="Production Manager", industry="Sweets & bakery", cats=["food"], home=False,
         quote="Packaging plays a big role in maintaining product presentation, especially in the sweets business. We appreciate Oxy Pack Global's efforts in delivering packaging that aligns with our requirements and their willingness to understand our needs."),
    dict(company="Vimal Healthy Oils", role="Procurement Head", industry="Edible oils & food processing", cats=["protective"], home=False,
         quote="We value suppliers who maintain consistency and understand the importance of quality. Our experience with Oxy Pack Global has been positive, with good coordination and a practical approach to packaging requirements."),
]
_LOGO = {c[0]: c for c in CLIENTS}
TESTI_RE = re.compile(r'<!-- testimonials -->.*?<!-- /testimonials -->\n?', re.S)


def tcard(t, compact=False):
    c = _LOGO.get(t["company"])
    logo = (f'<img src="assets/img/clients/{c[1]}" alt="" width="{c[2]}" height="{c[3]}" loading="lazy" decoding="async">'
            if c and c[1] else "")
    return (f'<figure class="tcard{" compact" if compact else ""}"><span class="tind">{e(t["industry"])}</span>'
            f'<blockquote><p>{e(t["quote"])}</p></blockquote>'
            f'<figcaption>{logo}<span><b>{e(t["company"])}</b><span>{e(t["role"])}</span></span></figcaption></figure>')


def testimonials_section(items, title, lead, soft=False):
    cls = "tgrid two" if len(items) == 2 else "tgrid"
    return (f'<!-- testimonials -->\n<section class="sec{" sec-soft" if soft else ""} testimonials" aria-labelledby="testi-h">\n<div class="wrap">\n'
            f'<div class="sec-head reveal"><div><p class="eyebrow">What customers say</p><h2 class="h2" id="testi-h">{e(title)}</h2>'
            f'<p class="lead" style="margin-top:16px">{e(lead)}</p></div></div>\n'
            f'<ul class="{cls}">' + "".join(f'<li>{tcard(t)}</li>' for t in items) + '</ul>\n</div>\n</section>\n<!-- /testimonials -->')


def cat_testimonials(key):
    return [t for t in TESTIMONIALS if key in t["cats"]]


HOW_WE_WORK = f'''<div class="info-card grid-lines">
<h2 style="color:#fff;font-size:21px;margin-bottom:22px">How ordering works</h2>
<ol style="margin:0;padding-left:20px;display:flex;flex-direction:column;gap:12px;color:#D3DBEA;line-height:1.5">
<li><b style="color:#fff">Share your requirement</b> — size, quantity, print and destination.</li>
<li><b style="color:#fff">Get a spec and quote</b> within one business day.</li>
<li><b style="color:#fff">Approve a sample</b> before production starts.</li>
<li><b style="color:#fff">We produce and ship</b> to your port, worldwide.</li>
</ol>
<dl style="margin:26px 0 0;padding-top:20px;border-top:1px solid rgba(255,255,255,.15)">
<dt>Email</dt><dd><a href="mailto:sales@oxypackglobal.com">sales@oxypackglobal.com</a></dd>
<dt>Phone / WhatsApp</dt><dd style="margin-bottom:0"><a href="tel:+919624449910">+91 96244 49910</a></dd>
</dl>
</div>'''


def cat_url(c):
    return f"{OUT_DIR}/{c['slug']}.html"


def prod_url(p):
    return f"{OUT_DIR}/{p['slug']}.html"


def credit(c):
    if "image_credit" not in c:
        return ""
    t, u, lic = c["image_credit"]
    return f'<p class="photo-credit">{e(t)}, <a href="{u}" rel="nofollow noopener" target="_blank">{lic}</a></p>'


# ---------- FAQs (shown on page and as FAQPage structured data) ----------
SAMPLE_ANSWER = ("Yes. We make a sample for fit, strength and print approval before bulk production starts, "
                 "so you know exactly what you will receive.")
EXPORT_REACH = ("We export to buyers in 20+ countries across Africa, the Middle East, Europe, the Americas and Asia-Pacific. "
                "We palletise and load the container and handle the export paperwork.")


def short_name(p):
    n = re.sub(r"\s*\(.*?\)", "", p["name"]).strip()
    return n[0].lower() + n[1:]


def faq_ld(items):
    return ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]})


def faq_section(items, title, soft=False, eyebrow="FAQ"):
    rows = "".join(f'<details class="faq-item"{" open" if i == 0 else ""}><summary>{e(q)}</summary><p>{e(a)}</p></details>'
                   for i, (q, a) in enumerate(items))
    return (f'<section class="sec{" sec-soft" if soft else ""}" id="faq">\n<div class="wrap faq-wrap">\n'
            f'<div class="reveal"><p class="eyebrow">{e(eyebrow)}</p><h2 class="h2">{e(title)}</h2>'
            f'<p class="lead" style="margin-top:16px">Can’t find your answer? Ask our export team — we reply within one business day.</p>'
            f'<div class="btn-row" style="margin-top:28px"><a href="contact.html" class="btn btn-navy" data-quote>Ask a question {ARROW}</a>'
            f'<a href="https://wa.me/{WA}" target="_blank" rel="noopener" class="btn btn-wa">{WA_ICON} WhatsApp</a></div></div>\n'
            f'<div class="faq">{rows}</div>\n</div>\n</section>')


def product_faqs(p):
    n = short_name(p)
    printing = dict(p["specs"]).get("Printing") or dict(CAT[p["cat"]]["specs"]).get("Printing", "flexo or offset printing")
    return [
        (f"What is the minimum order quantity for {n}?",
         f"The MOQ depends on size, material and printing — plain {n} usually have lower minimums than fully printed designs. "
         "Share your quantity in the quote form and we confirm the MOQ with your price."),
        (f"Can you print our logo and brand on {n}?",
         f"Yes. Every order is made to your specification, including your artwork and brand colours. Printing options: {printing}."),
        ("Can I get a sample before placing a bulk order?", SAMPLE_ANSWER),
        (f"Do you ship {n} to my country?", EXPORT_REACH),
        (f"What is the HS code for {n}?",
         f"{p['hs']} is the indicative HS code. The exact code depends on construction and your country's tariff schedule, "
         "so we confirm it for each order with our customs team."),
        ("How long does production take?",
         "Lead time depends on quantity, materials and printing. We confirm a dispatch date with your quote and keep you updated "
         "through production and pre-shipment quality checks."),
    ]


def category_faqs(c):
    names = [p["name"] for p in PRODUCTS if p["cat"] == c["key"]] + [t for t, _ in c["also"]]
    lname = c["name"].lower()
    return [
        (f"Which {lname} do you manufacture?",
         "Our range includes " + ", ".join(names[:-1]) + " and " + names[-1] + ". Every item is made to order to your size, material and print."),
        ("Do you make custom sizes and printed designs?",
         "Yes. We work from your dimensions, product weight and artwork, recommend the right paper specification, and share a sample for approval before bulk production."),
        ("Which countries do you export to?", EXPORT_REACH),
        ("Are your certifications suitable for international buyers?",
         "We work to ISO 9001 quality management, use FSC®-certified paper on request, and are an IEC-registered exporter. Food-contact grades are available for food packaging."),
        ("How do I get a price?",
         "Send your requirement through the quote form or WhatsApp. We reply within one business day with a recommended specification and price."),
    ]


# ---------- category pages ----------
def build_category(c):
    items = [p for p in PRODUCTS if p["cat"] == c["key"]]
    n = len(items)
    links = [("Home", "index.html"), ("Products", "products.html"), (c["name"], cat_url(c))]
    grid_cls = "pgrid" if n == 4 else "pgrid g3c"
    cards = "\n".join(pcard(p, prod_url(p)) for p in items)
    if n % 3 and n != 4:
        cards += (f'\n<li class="ccard navy"><div class="body"><h3>Need a different format?</h3>'
                  f'<p>Tell us what you ship and we\'ll engineer the right paper protection for it.</p>'
                  f'<a class="more" href="contact.html?cat={c["key"]}">Send your requirement {ARROW}</a></div></li>')
    also = "".join(f'<li>{BOX}<div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for t, d in c["also"])
    swap = ""
    if c.get("swap"):
        swap = ('<div class="swap-box" style="border:1px solid var(--line)"><h3 style="font-size:20px;margin-bottom:12px">Swap plastic for paper</h3>'
                + "".join(f'<div class="swap"><s>{e(a)}</s><b aria-hidden="true">→</b><span>{e(b)}</span></div>' for a, b in c["swap"])
                + '</div>')
    specs = "".join(f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td></tr>' for k, v in c["specs"])
    others = "".join(
        f'<a class="ccard mini" href="{cat_url(o)}"><img src="{o["image"]}" alt="" width="96" height="96" loading="lazy" decoding="async">'
        f'<div class="body"><h3>{e(o["name"])}</h3></div></a>'
        for o in CATEGORIES if o is not c)
    main = f'''<section class="page-hero dark grid-lines">
<img src="{c['hero']}" alt="" class="bg-img" fetchpriority="high" style="left:auto;right:0;width:45%;opacity:.35">
<div class="wrap">
{crumbs(links)}
<span class="pill">Made to order · Export ready</span>
<h1 style="margin-top:22px">{e(c['name'])}</h1>
<p>{e(c['intro'])}</p>
<div class="btn-row" style="margin-top:32px"><a href="#range" class="btn btn-green">See the range {DOWN}</a><a href="contact.html?cat={c['key']}" class="btn btn-ghost">Get a free quote</a></div>
{TRUST_ROW}
</div>
</section>

<section id="range" class="sec">
<div class="wrap">
<div class="sec-head reveal"><div>
<p class="eyebrow">The range</p>
<h2 class="h2">Products in this line</h2>
<p class="lead" style="margin-top:18px">{e(c.get('seo', ''))} Every item is made to order — your size, board grade and print. Open a product for its specifications and to request a quote.</p>
</div></div>
<ul class="{grid_cls}">
{cards}
</ul>
</div>
</section>

{testimonials_section(cat_testimonials(c['key']), "Trusted by brands like yours", "Feedback from customers who use our " + c['name'].lower() + ".", soft=True) if cat_testimonials(c['key']) else ""}
{LOGO_STRIP}
<section class="sec sec-soft">
<div class="wrap g2 start">
<div class="reveal"><div class="rel"><img src="{c['image']}" alt="{e(c['image_alt'])}" width="{c['image_w']}" height="{c['image_h']}" class="cover rounded" loading="lazy" decoding="async" style="height:400px"></div>
{credit(c)}
<table class="spec"><caption>Typical capabilities across this product line.</caption><tbody>{specs}</tbody></table></div>
<div class="reveal">
<p class="eyebrow">Capabilities</p>
<h2 class="h2" style="margin-bottom:20px">Also made in this line</h2>
<p class="lead">Beyond the products above, we make these to order:</p>
<ul class="items">{also}</ul>
{swap}
<a href="contact.html?cat={c['key']}" class="btn btn-navy" style="margin-top:32px">Quote {e(c['name'].lower())} {ARROW}</a>
</div>
</div>
</section>

{faq_section(category_faqs(c), c['name'] + " — common questions")}

<section class="sec sec-soft">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Explore more</p><h2 class="h2">Other product categories</h2></div><a href="products.html" class="link-u">All products →</a></div>
<div class="cgrid4">{others}</div>
</div>
</section>'''
    lds = [crumbs_ld(links), ld({"@context": "https://schema.org", "@type": "ItemList", "name": c["name"],
                                 "itemListElement": [{"@type": "ListItem", "position": i, "url": SITE + "/" + prod_url(p), "name": p["name"]}
                                                     for i, p in enumerate(items, 1)]}), faq_ld(category_faqs(c))]
    title = f"{c['name']} | Manufacturer & Exporter India"
    desc = f"{c['short']} Custom sizes and printing, samples before bulk orders, shipped worldwide. Get a free quote."
    page(cat_url(c), title, desc, main, lds, image=c["image"])


# ---------- product pages ----------
def build_product(p):
    c = CAT[p["cat"]]
    links = [("Home", "index.html"), ("Products", "products.html"), (c["name"], cat_url(c)), (p["name"], prod_url(p))]
    rel = [x for x in PRODUCTS if x["cat"] == p["cat"] and x is not p][:3]
    rel += [x for x in PRODUCTS if x["hot"] and x["cat"] != p["cat"]][:3 - len(rel)]
    wa = f"https://wa.me/{WA}?text=" + urllib.parse.quote(f"Hello OXY PACK GLOBAL, I'd like a quote for {p['name']}.")
    feats = "".join(f'<li>{TICK}<span>{e(f)}</span></li>' for f in p["features"])
    specs = "".join(f'<tr><th scope="row">{e(k)}</th><td>{e(v)}</td></tr>' for k, v in p["specs"])
    specs += f'<tr><th scope="row">HS code</th><td>{e(p["hs"])} (indicative)</td></tr>'
    apps = "".join(f'<span>{e(a)}</span>' for a in p["apps"])
    main = f'''<section class="page-hero pd dark grid-lines">
<div class="glow" style="right:-200px;top:-220px"></div>
<div class="wrap">
{crumbs(links)}
<div class="pd-grid">
<div>
<span class="pill">{e(c['name'])}</span>
<h1>{e(p['name'])}</h1>
<p>{e(p['short'])}</p>
<dl class="facts"><div><dt>HS code</dt><dd>{e(p['hs'])}</dd></div><div><dt>Top markets</dt><dd>{e(p['markets'])}</dd></div><div><dt>Supply</dt><dd>Made to order</dd></div></dl>
<div class="btn-row"><a href="#quote" class="btn btn-green">Get a free quote {ARROW}</a><a href="{e(wa)}" class="btn btn-ghost" target="_blank" rel="noopener">{WA_ICON} Ask on WhatsApp</a></div>
{TRUST_ROW}
</div>
<div class="pd-img">{'<span class="hot-tag">High demand</span>' if p['hot'] else ''}<img src="{p['img']}" alt="{e(p['alt'])}" width="640" height="480" fetchpriority="high"></div>
</div>
</div>
</section>

<section class="sec">
<div class="wrap g2 start">
<div class="reveal">
<p class="eyebrow">Overview</p>
<h2 class="h2" style="margin-bottom:20px">About this product</h2>
<p class="lead">{e(p['overview'])}</p>
<h3 style="font-size:20px;margin:36px 0 16px">Key features</h3>
<ul class="checks">{feats}</ul>
</div>
<div class="reveal">
<p class="eyebrow">Specifications</p>
<h2 class="h2">Typical specifications</h2>
<table class="spec"><caption>Typical values. The final specification is agreed with you for each order.</caption><tbody>{specs}</tbody></table>
<h3 style="font-size:20px;margin:36px 0 0">Used for</h3>
<div class="regions light">{apps}</div>
<a href="#quote" class="btn btn-navy" style="margin-top:36px">Quote this specification {ARROW}</a>
</div>
</div>
</section>

{LOGO_STRIP}
<section id="quote" class="sec sec-soft">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Request a quote</p><h2 class="h2">Get a price for this product</h2>
<p class="lead" style="margin-top:16px">Share your size, quantity and destination. We reply within one business day with a recommended specification and price.</p></div></div>
<div class="cgrid">
<div class="form-card">
{quote_form(f"Quote request — {p['name']}", CAT_INDEX[p['cat']], p['name'])}
</div>
<aside style="display:flex;flex-direction:column;gap:16px">{HOW_WE_WORK}{tcard((cat_testimonials(p['cat']) or TESTIMONIALS)[0], compact=True)}</aside>
</div>
</div>
</section>

{faq_section(product_faqs(p), "Questions about " + short_name(p))}

<section class="sec sec-soft">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Related products</p><h2 class="h2">You may also need</h2></div><a href="{cat_url(c)}" class="link-u">All {e(c['name'].lower())} →</a></div>
<ul class="pgrid g3c">
{chr(10).join(pcard(x, prod_url(x)) for x in rel)}
</ul>
</div>
</section>'''
    lds = [crumbs_ld(links), ld({"@context": "https://schema.org", "@type": "Product", "name": p["name"],
                                 "description": p["overview"], "image": SITE + "/" + p["img"], "category": c["name"],
                                 "brand": {"@type": "Brand", "name": "OXY PACK GLOBAL"}, "url": SITE + "/" + prod_url(p)}),
           faq_ld(product_faqs(p))]
    sn = re.sub(r"\s*\(.*?\)", "", p["name"]).strip()
    page(prod_url(p), f"{sn[0].upper() + sn[1:]} | Manufacturer & Exporter India",
         f"{p['short']} Custom sizes and printing, samples before bulk orders, shipped worldwide. Get a free quote.",
         main, lds, image=p["img"], band=False)


# ---------- products overview ----------
def build_overview():
    jump = "".join(f'<a href="{cat_url(c)}"><span>{e(c["name"])}</span></a>' for c in CATEGORIES)
    cards = []
    for c in CATEGORIES:
        items = [p for p in PRODUCTS if p["cat"] == c["key"]]
        lis = "".join(f"<li>{e(p['name'])}</li>" for p in items)
        cards.append(f'<a class="ccard reveal" href="{cat_url(c)}"><img src="{c["image"]}" alt="{e(c["image_alt"])}" width="{c["image_w"]}" height="{c["image_h"]}" loading="lazy" decoding="async">'
                     f'<div class="body"><h2>{e(c["name"])}</h2><p>{e(c["short"])}</p><ul>{lis}</ul>'
                     f'<span class="more">View category {ARROW}</span></div></a>')
    cards.append(f'<div class="ccard navy reveal"><div class="body"><span class="num" style="color:var(--green-300)">CUSTOM</span><h2>Need something not listed?</h2>'
                 f'<p>Send us your product, size and destination. We\'ll engineer the right paper packaging for it.</p>'
                 f'<a class="more" href="contact.html">Send your requirement {ARROW}</a></div></div>')
    hot = "\n".join(pcard(p, prod_url(p)) for p in PRODUCTS if p["hot"])
    redirect = ("<script>(function(){var m={" + ",".join(f'"#{k}":"{cat_url(CAT[v])}"' for k, v in
                {"corrugated": "corrugated", "cartons": "cartons", "bags": "bags", "protective": "protective", "food": "food"}.items())
                + "};if(m[location.hash])location.replace(m[location.hash]);})()</script>\n")
    main = f'''<section class="page-hero dark grid-lines">
<img src="assets/img/corrugated-shipping-carton.jpg" alt="" width="1050" height="1400" class="bg-img" fetchpriority="high" style="left:auto;right:0;width:45%;opacity:.35">
<div class="wrap" style="padding-bottom:0">
<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="index.html">Home</a></li><li aria-current="page">Products</li></ol></nav>
<span class="pill">100% paper · 0% plastic</span>
<h1 style="margin-top:22px">Paper packaging, engineered for export.</h1>
<p>Five product lines, all made to order — your dimensions, your board grade, your print. Pick a category to see the range.</p>
<nav class="jump" aria-label="Product categories">{jump}</nav>
</div>
</section>

{LOGO_STRIP}
<section id="categories" class="sec">
<div class="wrap">
<div class="sec-head reveal"><div>
<p class="eyebrow">Product categories</p>
<h2 class="h2">Choose a product line</h2>
<p class="lead" style="margin-top:18px">Each category lists its products, typical specifications and what else we make to order.</p>
</div></div>
<div class="cgrid3">
{chr(10).join(cards)}
</div>
</div>
</section>

<section class="sec sec-soft">
<div class="wrap">
<div class="sec-head reveal"><div>
<p class="eyebrow">Export best-sellers</p>
<h2 class="h2">High-demand products</h2>
<p class="lead" style="margin-top:18px">The paper packaging overseas buyers order most from India.</p>
</div><a href="contact.html" class="link-u">Need a custom product? Ask us →</a></div>
<ul class="pgrid g3c">
{hot}
</ul>
<p class="pnote">HS codes are indicative. We confirm the exact classification for each order with our customs team. Product photos are representative (via <a href="https://www.pexels.com/license/" rel="nofollow noopener" target="_blank" style="color:#6B7486">Pexels</a>); every order is made to your specification.</p>
</div>
</section>'''
    lds = [crumbs_ld([("Home", ""), ("Products", "products.html")]),
           ld({"@context": "https://schema.org", "@type": "ItemList", "name": "OXY PACK GLOBAL product categories",
               "itemListElement": [{"@type": "ListItem", "position": i, "url": SITE + "/" + cat_url(c), "name": c["name"]}
                                   for i, c in enumerate(CATEGORIES, 1)]})]
    page("products.html", "Paper Packaging Products: Boxes, Bags, Cartons & Food Packaging | OXY PACK GLOBAL",
         "Browse 5 paper packaging lines: corrugated boxes, paper bags & sacks, printed cartons & gift boxes, food service packaging and protective packaging. Made to order in India, exported worldwide.",
         main, lds, extra=redirect)


PROD = {p['slug']: p for p in PRODUCTS}


# ---------- export page ----------
EXPORT_FAQS = [
    ("How do I start an order as an overseas buyer?",
     "Send your product, size, quantity and destination through the quote form or WhatsApp. We reply within one business day with a recommended specification and price, then share a sample for approval before production."),
    ("Which countries do you ship to?",
     "We export to buyers in 20+ countries across Africa, the Middle East, Europe, the Americas and Asia-Pacific, by sea from India's west-coast ports."),
    ("Can you ship full containers and smaller orders?",
     "Yes. We ship full container loads and can also arrange smaller shipments, so you can start with a trial order."),
    ("Do you check quality before shipping?",
     "Yes. We work to ISO 9001 processes, run batch tests for bursting strength, edge crush, compression and moisture where relevant, and share pre-shipment inspection reports before loading."),
    ("Can you ship different products in one container?",
     "Yes. Boxes, bags, cartons and protective packaging can be combined into one container to save freight."),
    ("Can you print our artwork and languages?",
     "Yes. Every order is printed from your artwork, including multilingual and Arabic text, with colour matching before production."),
]

# ---------- market landing pages ----------
MARKETS = [
    dict(
        slug="uae-gcc-paper-packaging", short="UAE & GCC",
        name="UAE & GCC", title="Paper Packaging Supplier for UAE & GCC | From India",
        description="Paper cups, food boxes, bagasse tableware, carry bags, gift boxes and export cartons made in India for buyers in the UAE, Saudi Arabia, Oman, Qatar, Kuwait and Bahrain.",
        h1="Paper packaging for the <em>UAE & GCC.</em>",
        intro="We manufacture plastic-free paper packaging in Gujarat, India — a short sea crossing from the Gulf — for cafés, restaurant chains, retailers, gifting brands and distributors across the UAE and GCC.",
        hero="assets/img/export-container-port.jpg",
        countries=["UAE", "Saudi Arabia", "Oman", "Qatar", "Kuwait", "Bahrain"],
        reasons=[
            ("Close to the Gulf", "We ship from India's west coast, a short sea route to Jebel Ali and other Gulf ports."),
            ("India–UAE CEPA", "The India–UAE Comprehensive Economic Partnership Agreement, in force since May 2022, can lower import duty on qualifying goods."),
            ("Ready for plastic bans", "Paper cups, bowls, food boxes, straws and bags that replace the single-use plastics now restricted in the UAE and Oman."),
            ("Built for your brand", "Printed from your artwork in English and Arabic, with premium finishes for sweets, dates, perfume and gifting."),
        ],
        rules=[
            "<strong>UAE:</strong> a nationwide ban on single-use plastic bags has applied since 1 January 2024. From 1 January 2026 it was extended to single-use plastic cups and lids, cutlery, plates, straws, stirrers and food containers.",
            "<strong>Dubai:</strong> the final phase of Dubai's single-use products regulation took effect on 1 January 2026.",
            "<strong>Oman:</strong> a phased ban on plastic shopping bags reached its fifth phase on 1 July 2026, with the aim of eliminating them nationwide by 2027.",
        ],
        products=["paper-cups", "kraft-takeaway-boxes", "moulded-fibre-tableware", "kraft-carry-bags", "rigid-gift-boxes", "corrugated-export-cartons"],
        industries=["Cafés & coffee chains", "Restaurants & QSR", "Cloud kitchens", "Catering & airlines", "Retail & malls",
                    "Dates, sweets & bakeries", "Perfume & gifting", "Logistics & re-export"],
        testimonials=["Bikaji", "Shubha", "Vijay Mamra"],
        faqs=[
            ("Do you supply packaging to Dubai, Abu Dhabi and Saudi Arabia?",
             "Yes. We ship to buyers across the UAE, Saudi Arabia, Oman, Qatar, Kuwait and Bahrain, by sea from India's west coast to the main Gulf ports."),
            ("Do you have paper alternatives to the plastics banned in the UAE?",
             "Yes. We make paper cups and lids, paper bowls, kraft food boxes, bagasse plates and containers, paper straws and paper carry bags. Please confirm the requirements for your specific product with your local authority."),
            ("Can you print Arabic and English on our packaging?",
             "Yes. We print from your artwork, including Arabic and bilingual designs, and match your brand colours before production."),
            ("Do you make premium boxes for dates, sweets and perfume?",
             "Yes. Rigid gift boxes, folding cartons and paper tubes with foil, embossing and spot UV are among our most popular products for Gulf gifting brands."),
            ("Can I see a sample before ordering?",
             "Yes. We make a sample for fit, strength and print approval before bulk production starts."),
        ],
    ),
    dict(
        slug="east-africa-paper-packaging", short="East Africa",
        name="East Africa", title="Paper Packaging Supplier for Kenya & East Africa | From India",
        description="Paper carry bags, SOS bags, multiwall sacks, corrugated cartons and food boxes made in India for buyers in Kenya, Tanzania, Uganda and Rwanda.",
        h1="Paper packaging for <em>East Africa.</em>",
        intro="Africa was our first export market. We supply paper bags, sacks, corrugated cartons and food packaging to retailers, millers, fresh-produce exporters and distributors across Kenya, Tanzania, Uganda and Rwanda.",
        hero="assets/img/export-cartons-forklift.jpg",
        countries=["Kenya", "Tanzania", "Uganda", "Rwanda"],
        reasons=[
            ("Our first export market", "We have shipped to African buyers from our early years and understand the region's requirements."),
            ("Direct sea routes", "Regular sailings from India's west coast to Mombasa and Dar es Salaam, the gateways for Kenya, Tanzania, Uganda and Rwanda."),
            ("Plastic-bag ban ready", "Kraft carry bags and SOS bags that replace the plastic bags banned in Kenya, Tanzania and Rwanda."),
            ("Strong for heavy loads", "Multiwall sacks and 5 or 7-ply cartons for flour, cement, feed, fresh produce and long inland journeys."),
        ],
        rules=[
            "<strong>Kenya:</strong> plastic carrier bags have been banned since August 2017, and single-use plastics have been banned in protected areas since 2020.",
            "<strong>Tanzania:</strong> plastic carrier bags have been banned since June 2019.",
            "<strong>Rwanda:</strong> has one of the world's strictest bans on plastic bags and single-use plastics.",
            "<strong>Regional:</strong> an East African Community bill to restrict single-use plastics across the region has been proposed.",
        ],
        products=["kraft-carry-bags", "sos-grocery-bags", "multiwall-paper-sacks", "corrugated-export-cartons", "heavy-duty-boxes", "kraft-takeaway-boxes"],
        industries=["Supermarkets & retail", "Flour, cement & feed millers", "Flower & fresh-produce exporters", "Tea & coffee",
                    "FMCG distributors", "Restaurants & QSR", "Pharmaceuticals", "Agriculture & agri-inputs"],
        testimonials=["Alpha Crop Care", "Primeseal Straps", "Vimal Healthy Oils"],
        faqs=[
            ("Do you ship to Mombasa and Dar es Salaam?",
             "Yes. We ship by sea from India's west coast to Mombasa and Dar es Salaam, the main ports serving Kenya, Tanzania, Uganda and Rwanda."),
            ("Are your paper bags an alternative to banned plastic bags?",
             "Yes. Our kraft carry bags and SOS grocery bags are made entirely from paper. Please confirm the requirements for your specific use with your local authority."),
            ("Do you make sacks for flour, maize, cement or animal feed?",
             "Yes. We make 2 to 4-ply multiwall paper sacks for 10–50 kg fills, in valve or open-mouth styles, printed with your brand and product information."),
            ("Can you supply cartons for flowers, avocados and fresh produce?",
             "Yes. We make corrugated cartons with vent holes and water-resistant coatings, sized and rated for your produce and cold-chain shipping."),
            ("Can I see a sample before ordering?",
             "Yes. We make a sample for fit, strength and print approval before bulk production starts."),
        ],
    ),
]


def market_url(m):
    return f"markets/{m['slug']}.html"


def market_cards():
    return "".join(
        f'<a class="ccard reveal" href="{market_url(m)}"><img src="{m["hero"]}" alt="" width="1024" height="640" loading="lazy" decoding="async">'
        f'<div class="body"><span class="num">EXPORT MARKET</span><h3>Paper packaging for {e(m["name"])}</h3>'
        f'<p>{e(", ".join(m["countries"]))}</p><span class="more">Explore {e(m["short"])} {ARROW}</span></div></a>' for m in MARKETS)


def build_market(m):
    links = [("Home", "index.html"), ("Export", "export.html"), (m["name"], market_url(m))]
    wa = f"https://wa.me/{WA}?text=" + urllib.parse.quote(f"Hello OXY PACK GLOBAL, I'm a buyer in {m['name']} and would like a quote.")
    prods = [PROD[s] for s in m["products"] if s in PROD]
    tests = [t for t in TESTIMONIALS if t["company"] in m["testimonials"]]
    others = [o for o in MARKETS if o is not m]
    plain_h1 = re.sub(r"<.*?>", "", m["h1"])
    main = f'''<section class="page-hero dark grid-lines">
<img src="{m['hero']}" alt="" class="bg-img" fetchpriority="high" style="opacity:.22">
<div class="glow" style="right:-160px;top:-200px"></div>
<div class="wrap">
{crumbs(links)}
<span class="pill">Export market · {e(" · ".join(m["countries"][:4]))}</span>
<h1 style="margin-top:22px">{m['h1']}</h1>
<p>{e(m['intro'])}</p>
<div class="btn-row" style="margin-top:32px"><a href="#quote" class="btn btn-green">Get a free quote {ARROW}</a><a href="{e(wa)}" class="btn btn-ghost" target="_blank" rel="noopener">{WA_ICON} Talk to export sales</a></div>
{TRUST_ROW}
</div>
</section>

<section class="sec">
<div class="wrap">
<div class="sec-head reveal"><div><p class="eyebrow">Why buyers in {e(m['short'])} choose us</p><h2 class="h2">Your paper packaging partner in India</h2></div></div>
<div class="g4">{"".join(f'<div class="soft-card reveal"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in m["reasons"])}</div>
</div>
</section>

<section class="sec sec-soft">
<div class="wrap g2 start">
<div class="reveal">
<p class="eyebrow">Moving away from plastic</p>
<h2 class="h2" style="margin-bottom:20px">Why demand for paper is growing in {e(m['short'])}</h2>
<p class="lead">Governments across the region are restricting single-use plastics — and businesses need reliable paper alternatives.</p>
<ul class="checks" style="margin-top:24px">{"".join(f'<li>{TICK}<span>{r}</span></li>' for r in m["rules"])}</ul>
</div>
<div class="reveal">
<p class="eyebrow">Industries we serve</p>
<h2 class="h2" style="margin-bottom:20px">Who we supply in {e(m['short'])}</h2>
<div class="regions light">{"".join(f'<span>{e(i)}</span>' for i in m["industries"])}</div>
<p style="margin-top:28px;font-size:15px;color:var(--muted)">Countries we ship to in the region: {e(", ".join(m["countries"]))}.</p>
<a href="#quote" class="btn btn-navy" style="margin-top:28px">Tell us what you need {ARROW}</a>
</div>
</div>
</section>

<section class="sec">
<div class="wrap">
<div class="sec-head reveal"><div><p class="eyebrow">Popular in {e(m['short'])}</p><h2 class="h2">Packaging we supply to the region</h2></div><a href="products.html" class="link-u">All products →</a></div>
<ul class="pgrid g3c">
{chr(10).join(pcard(x, prod_url(x)) for x in prods)}
</ul>
</div>
</section>

{LOGO_STRIP}
{testimonials_section(tests, "What our customers say", "Brands that rely on our packaging and coordination.", soft=True) if tests else ""}

{faq_section(m['faqs'], "Buying from us in " + m['short'] + " — common questions")}

<section id="quote" class="sec sec-soft">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Request a quote</p><h2 class="h2">Get a quote for {e(m['short'])}</h2>
<p class="lead" style="margin-top:16px">Tell us the product, quantity and destination. We reply within one business day with a recommended specification and price.</p></div></div>
<div class="cgrid">
<div class="form-card">
{quote_form("Quote request — " + m['name'] + " market page")}
</div>
<aside style="display:flex;flex-direction:column;gap:16px">{HOW_WE_WORK}{"".join(f'<a class="ccard mini" href="{market_url(o)}"><div class="body"><span class="tind">Other market</span><h3>Paper packaging for {e(o["name"])}</h3></div></a>' for o in others)}<a class="ccard mini" href="export.html"><div class="body"><span class="tind">Exporting</span><h3>How we export worldwide</h3></div></a></aside>
</div>
</div>
</section>'''
    lds = [crumbs_ld(links), faq_ld(m["faqs"])]
    page(market_url(m), m["title"], m["description"], main, lds, image=m["hero"], band=False, active="export.html")


def build_export():
    links = [("Home", "index.html"), ("Export", "export.html")]
    who = [("Importers & distributors", "Container loads of standard and custom packaging for your local market."),
           ("Brands & manufacturers", "Branded boxes, bags and cartons made to your specification and artwork."),
           ("Retail & e-commerce", "Mailer boxes, carry bags and paper void fill that replace plastic."),
           ("Food service chains", "Food-grade cups, bowls, takeaway boxes and wraps for cafés and restaurants.")]
    steps = [("Enquiry & brief", "Share size, weight, quantity and destination. Get a recommendation and quote within one business day."),
             ("Sample & approval", "Dieline and physical sample for fit, strength and print sign-off."),
             ("Production", "Scheduled manufacturing with a confirmed dispatch date and regular updates."),
             ("Quality check", "Batch testing and pre-shipment inspection reports shared before loading."),
             ("Shipping", "Palletised, container-loaded and shipped to your port with the export paperwork handled.")]
    why = [("Made to order", "Your dimensions, board grade, print and quantity — not off-the-shelf stock."),
           ("Certified quality", "ISO 9001 processes, FSC®-certified paper and an IEC-registered exporter."),
           ("100% paper", "Plastic-free packaging for brands and markets moving away from single-use plastic."),
           ("One partner", "Design, printing, production, testing and shipping under one roof."),
           ("Samples first", "Approve a physical sample before we start bulk production."),
           ("Fast answers", "A reply within one business day, by email or WhatsApp.")]
    home_t = [t for t in TESTIMONIALS if t["company"] in ("Shubha", "Nuvela Pharma", "Primeseal Straps")]
    main = f'''<section class="page-hero dark grid-lines">
<img src="assets/img/export-container-port.jpg" alt="" width="1024" height="576" class="bg-img" fetchpriority="high" style="opacity:.22">
<div class="glow" style="right:-160px;top:-200px"></div>
<div class="wrap">
{crumbs(links)}
<span class="pill">Export packaging partner · Since 2017</span>
<h1 style="margin-top:22px">Paper packaging from India, <em>shipped to your port.</em></h1>
<p>We manufacture custom paper packaging in Rajkot, India and export it to businesses in 20+ countries — with samples first, quality checks before loading, and the export paperwork handled.</p>
<div class="btn-row" style="margin-top:32px"><a href="#quote" class="btn btn-green">Get a free export quote {ARROW}</a><a href="https://wa.me/{WA}" class="btn btn-ghost" target="_blank" rel="noopener">{WA_ICON} Talk to export sales</a></div>
{TRUST_ROW}
</div>
</section>

<section class="sec">
<div class="wrap">
<div class="sec-head reveal"><div><p class="eyebrow">Who we supply</p><h2 class="h2">Packaging for every business that ships</h2>
<p class="lead" style="margin-top:16px">Whatever you sell and wherever you sell it, we make the paper packaging and deliver it to your port.</p></div></div>
<div class="g4">{"".join(f'<div class="soft-card reveal"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in who)}</div>
</div>
</section>

<section class="sec dark grid-lines rel ovh">
<img src="assets/img/shipping-port-aerial.jpg" alt="" width="1024" height="683" class="bg-img" loading="lazy" decoding="async" style="opacity:.14">
<div class="wrap rel">
<div class="g2" style="align-items:end;margin-bottom:56px">
<div><p class="eyebrow">How it works</p><h2 class="h2">From enquiry to your port in five steps</h2></div>
<div><p class="lead">Shipping to buyers across these regions:</p><div class="regions"><span class="on">Africa</span><span>Middle East</span><span>Europe</span><span>Americas</span><span>Asia-Pacific</span></div></div>
</div>
<ol class="g5" style="list-style:none;margin:0;padding:0">{"".join(f'<li class="step{" hl" if i == 5 else ""} reveal"><strong>0{i}</strong><h3>{e(a)}</h3><p>{e(b)}</p></li>' for i, (a, b) in enumerate(steps, 1))}</ol>
</div>
</section>

<section class="sec" id="markets">
<div class="wrap">
<div class="sec-head reveal"><div><p class="eyebrow">Markets we serve</p><h2 class="h2">Packaging for your region</h2>
<p class="lead" style="margin-top:16px">See the products, industries and regulations that matter most in your market.</p></div></div>
<div class="cgrid3">{market_cards()}<div class="ccard navy reveal"><div class="body"><span class="num" style="color:var(--green-300)">OTHER COUNTRIES</span><h3>Shipping somewhere else?</h3><p>We export to 20+ countries across Africa, the Middle East, Europe, the Americas and Asia-Pacific.</p><a class="more" href="#quote">Ask for a quote {ARROW}</a></div></div></div>
</div>
</section>

<section class="sec sec-soft">
<div class="wrap">
<div class="sec-head reveal"><div><p class="eyebrow">Why buyers choose us</p><h2 class="h2">An export partner, not just a box maker</h2></div></div>
<div class="g3">{"".join(f'<div class="card reveal" style="padding:28px"><h3 style="margin-top:0">{e(a)}</h3><p>{e(b)}</p></div>' for a, b in why)}</div>
</div>
</section>

{LOGO_STRIP}
{testimonials_section(home_t, "What our customers say", "Brands that rely on our packaging and coordination.")}

{faq_section(EXPORT_FAQS, "Exporting with us — common questions", soft=True)}

<section id="quote" class="sec">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Request a quote</p><h2 class="h2">Get your export quote</h2>
<p class="lead" style="margin-top:16px">Tell us what you need and where it's going. We reply within one business day with a specification and price.</p></div></div>
<div class="cgrid">
<div class="form-card">
{quote_form("Export quote request — export page")}
</div>
<aside>{HOW_WE_WORK}</aside>
</div>
</div>
</section>'''
    lds = [crumbs_ld(links), faq_ld(EXPORT_FAQS)]
    page("export.html", "Paper Packaging Exporter from India — Worldwide Shipping | OXY PACK GLOBAL",
         "Custom paper packaging made in India and shipped to 20+ countries. Samples before bulk orders, quality checks before loading. Get a free export quote.",
         main, lds, image="assets/img/export-container-port.jpg", band=False, active="export.html")


# ---------- buyer guides ----------
try:
    from guides_data import GUIDES  # noqa: E402
except ImportError:
    GUIDES = []
GUIDE_IMG = {"import-paper-packaging-from-india": "assets/img/export-container-port.jpg",
             "3-ply-vs-5-ply-vs-7-ply-corrugated-boxes": "assets/img/corrugated-box-open.jpg",
             "hs-codes-for-paper-packaging": "assets/img/export-cartons-forklift.jpg"}
GUIDE_DATE = "2026-11-19"
PROD = {p["slug"]: p for p in PRODUCTS}


def guide_url(g):
    return f"guides/{g['slug']}.html"


def build_guide(g):
    links = [("Home", "index.html"), ("Buyer guides", "guides.html"), (g["h1"], guide_url(g))]
    img = GUIDE_IMG.get(g["slug"], "assets/img/og-image.jpg")
    rel = [PROD[s] for s in g.get("related", []) if s in PROD][:3]
    others = [x for x in GUIDES if x is not g]
    toc = "".join(f'<li><a href="#s{i}">{re.sub("<.*?>", "", h)}</a></li>'
                  for i, h in enumerate(re.findall(r"<h2>(.*?)</h2>", g["body"]), 1))
    n = iter(range(1, 100))
    body = re.sub(r"<h2>", lambda m: f'<h2 id="s{next(n)}">', g["body"])
    body = body.replace("<table>", '<div class="table-wrap"><table class="itable">').replace("</table>", "</table></div>")
    main = f'''<section class="page-hero dark grid-lines">
<img src="{img}" alt="" class="bg-img" fetchpriority="high" style="opacity:.18">
<div class="wrap" style="padding-top:72px;padding-bottom:72px">
{crumbs(links)}
<span class="pill">Buyer guide · {g['read_time']} min read</span>
<h1 style="margin-top:22px;max-width:960px">{e(g['h1'])}</h1>
<p>{e(g['intro'])}</p>
</div>
</section>

<section class="sec guide-sec">
<div class="wrap guide-grid">
<article class="prose">{body}</article>
<aside class="guide-aside">
<div class="toc"><p class="eyebrow">In this guide</p><ol>{toc}</ol></div>
<div class="info-card grid-lines"><h2 style="color:#fff;font-size:20px;margin-bottom:10px">Need packaging quoted?</h2>
<p style="color:#D3DBEA;font-size:15px;line-height:1.6;margin-bottom:20px">Send your size, quantity and destination. We reply within one business day.</p>
<a href="#quote" class="btn btn-green" style="width:100%;justify-content:center">Get a free quote</a>
<a href="https://wa.me/{WA}" target="_blank" rel="noopener" class="btn btn-outline-light" style="width:100%;justify-content:center;margin-top:10px">{WA_ICON} WhatsApp us</a></div>
</aside>
</div>
</section>

{faq_section(g['faqs'], "Frequently asked questions", soft=True)}

{('<section class="sec"><div class="wrap"><div class="sec-head"><div><p class="eyebrow">Related products</p><h2 class="h2">Packaging mentioned in this guide</h2></div></div><ul class="pgrid g3c">' + "".join(pcard(x, prod_url(x)) for x in rel) + '</ul></div></section>') if rel else ''}

{LOGO_STRIP}
<section id="quote" class="sec sec-soft">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Request a quote</p><h2 class="h2">Ready to source your packaging?</h2>
<p class="lead" style="margin-top:16px">Tell us what you need. We reply within one business day with a recommended specification and price.</p></div></div>
<div class="cgrid">
<div class="form-card">
{quote_form("Quote request — guide: " + g['h1'])}
</div>
<aside style="display:flex;flex-direction:column;gap:16px">{HOW_WE_WORK}{"".join(f'<a class="ccard mini" href="{guide_url(o)}"><div class="body"><span class="tind">More guides</span><h3>{e(o["h1"])}</h3></div></a>' for o in others)}</aside>
</div>
</div>
</section>'''
    article = {"@context": "https://schema.org", "@type": "Article", "headline": g["h1"], "description": g["description"],
               "image": SITE + "/" + img, "datePublished": GUIDE_DATE, "dateModified": GUIDE_DATE,
               "author": {"@type": "Organization", "name": "OXY PACK GLOBAL", "url": SITE + "/"},
               "publisher": {"@type": "Organization", "name": "OXY PACK GLOBAL",
                             "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/oxy-pack-global-logo.png"}},
               "mainEntityOfPage": SITE + "/" + guide_url(g)}
    page(guide_url(g), f"{g['title']} | OXY PACK GLOBAL", g["description"], main,
         [crumbs_ld(links), ld(article), faq_ld(g["faqs"])], image=img, band=False, active="", og_type="article")


def guide_cards(prefix_link=True):
    return "".join(
        f'<a class="ccard reveal" href="{guide_url(g)}"><img src="{GUIDE_IMG.get(g["slug"], "assets/img/og-image.jpg")}" alt="" width="1024" height="640" loading="lazy" decoding="async">'
        f'<div class="body"><span class="num">BUYER GUIDE · {g["read_time"]} MIN READ</span><h3>{e(g["h1"])}</h3><p>{e(g["intro"])}</p>'
        f'<span class="more">Read the guide {ARROW}</span></div></a>' for g in GUIDES)


def build_guides_index():
    links = [("Home", "index.html"), ("Buyer guides", "guides.html")]
    main = f'''<section class="page-hero dark grid-lines">
<div class="glow" style="right:-160px;top:-200px"></div>
<div class="wrap">
{crumbs(links)}
<span class="pill">Resources for importers</span>
<h1 style="margin-top:22px">Packaging buyer guides</h1>
<p>Practical, no-nonsense guides for businesses sourcing paper packaging from India — from choosing box strength to HS codes and shipping terms.</p>
</div>
</section>
<section class="sec">
<div class="wrap">
<div class="cgrid3">{guide_cards()}</div>
</div>
</section>
{LOGO_STRIP}
<section class="sec sec-soft"><div class="wrap" style="text-align:center">
<h2 class="h2">Have a packaging question we haven't covered?</h2>
<p class="lead" style="margin:16px auto 28px;max-width:640px">Our export team answers buyer questions every day. Ask us anything — we reply within one business day.</p>
<div class="btn-row" style="justify-content:center"><a href="contact.html" class="btn btn-green" data-quote>Ask our team {ARROW}</a><a href="https://wa.me/{WA}" target="_blank" rel="noopener" class="btn btn-wa">{WA_ICON} WhatsApp</a></div>
</div></section>'''
    lds = [crumbs_ld(links), ld({"@context": "https://schema.org", "@type": "ItemList", "name": "Packaging buyer guides",
                                 "itemListElement": [{"@type": "ListItem", "position": i, "url": SITE + "/" + guide_url(g), "name": g["h1"]}
                                                     for i, g in enumerate(GUIDES, 1)]})]
    page("guides.html", "Packaging Buyer Guides for Importers | OXY PACK GLOBAL",
         "Free guides for businesses buying paper packaging from India: importing step by step, corrugated box strength, HS codes and shipping terms.",
         main, lds, active="")


GUIDES_RE = re.compile(r'<!-- guides -->.*?<!-- /guides -->\n?', re.S)


def home_guides_section():
    if not GUIDES:
        return ""
    return ('<!-- guides -->\n<section class="sec sec-soft">\n<div class="wrap">\n'
            '<div class="sec-head reveal"><div><p class="eyebrow">Buyer guides</p><h2 class="h2">Sourcing packaging from India? Start here.</h2></div>'
            '<a href="guides.html" class="link-u">All guides →</a></div>\n'
            f'<div class="cgrid3">{guide_cards()}</div>\n</div>\n</section>\n<!-- /guides -->')


# ---------- updates to hand-written pages ----------
def update_root_pages():
    for name in ["index.html", "about.html", "industries.html", "contact.html", "404.html"]:
        s = read(name)
        s = FOOTER_RE.sub(lambda m: FOOTER_PRODUCTS, s)
        write(name, s)
    s = read("contact.html")
    s = re.sub(r'<select id="category" name="category">.*?</select>',
               '<select id="category" name="category">' + "".join(f"<option>{e(o)}</option>" for o in SELECT_OPTS) + '</select>', s)
    s = CLIENTS_RE.sub("", s)
    s = s.replace("</main>", LOGO_STRIP + "\n</main>", 1)
    s = TESTI_RE.sub("", s)
    anchor = '<div class="card" style="padding:32px">'
    assert s.count(anchor) == 1, "contact aside not found"
    s = s.replace(anchor, "<!-- testimonials -->" + tcard(TESTIMONIALS[0], compact=True) + "<!-- /testimonials -->\n" + anchor)
    write("contact.html", s)


def update_home():
    s = read("index.html")
    s = CLIENTS_RE.sub("", s)
    s = TESTI_RE.sub("", s)
    s, k = re.subn(r'(<div class="marquee-wrap"[^\n]*\n)', lambda m: m[1] + "\n" + CLIENTS_GRID + "\n", s, count=1)
    assert k == 1, "marquee not found"
    tiles = [("corrugated", "assets/img/corrugated-shipping-carton.jpg", 1050, 1400, "Corrugated cardboard shipping carton", True),
             ("cartons", "assets/img/kraft-gift-boxes.jpg", 1024, 683, "Kraft gift boxes with printed paper tape", False),
             ("bags", "assets/img/kraft-paper-carry-bags.jpg", 1400, 1100, "Brown kraft and white paper carry bags", False),
             ("food", "assets/img/products/13-paper-cups.jpg", 640, 480, "Kraft paper cups", False),
             ("protective", "assets/img/paper-protective-packaging-gift-box.jpg", 1280, 853, "Bottle cushioned with paper fill inside a box", False)]
    out = []
    for key, img, w, h, alt, big in tiles:
        c = CAT[key]
        out.append(f'<a href="{cat_url(c)}" class="tile{" big" if big else ""} reveal"><img src="{img}" alt="{e(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async">'
                   f'<div class="txt"><h3>{e(c["name"])}</h3><p>{e(c["short"])}</p></div></a>')
    s, k = re.subn(r'(<div class="bento">\n).*?(\n</div>\n</div>\n</section>)', lambda m: m[1] + "\n".join(out) + m[2], s, count=1, flags=re.S)
    assert k == 1, "bento not found"
    s = s.replace("Four paper product lines. Every shipping need covered.", "Five paper product lines. Every shipping need covered.")
    form_section = f'''<section id="quote" class="sec sec-soft">
<div class="wrap qgrid">
<div class="reveal">
<p class="eyebrow">Request a quote</p>
<h2 class="h2" style="margin-bottom:20px">Planning your next shipment?</h2>
<p class="lead">Send us your specs — we reply with a recommended paper specification and price within one business day.</p>
<ul class="checks" style="margin:28px 0 32px">
<li>{TICK}<span>Custom sizes, board grades and printing</span></li>
<li>{TICK}<span>Samples before bulk production</span></li>
<li>{TICK}<span>Shipping to 20+ countries worldwide</span></li>
</ul>
<div class="info-card grid-lines">
<dl style="margin:0">
<dt>Email</dt><dd><a href="mailto:sales@oxypackglobal.com">sales@oxypackglobal.com</a></dd>
<dt>Phone / WhatsApp</dt><dd><a href="tel:+919624449910">+91 96244 49910</a> · <a href="https://wa.me/{WA}" target="_blank" rel="noopener">Chat on WhatsApp</a></dd>
<dt>Hours</dt><dd style="margin-bottom:0">Mon–Sat, 9:30–18:30 IST</dd>
</dl>
</div>
</div>
<div class="form-card reveal">
{quote_form("New quote request — homepage")}
</div>
</div>
</section>'''
    if 'id="quote"' in s:
        s, k = re.subn(r'<section id="quote" class="sec sec-soft">.*?</section>', lambda m: form_section, s, count=1, flags=re.S)
    else:
        s, k = re.subn(r'<section class="sec">\n<div class="wrap">\n<div class="cta-box grid-lines">.*?</section>', lambda m: form_section, s, count=1, flags=re.S)
    assert k == 1, "home CTA section not found"
    home_t = testimonials_section([t for t in TESTIMONIALS if t["home"]], "Brands that rely on our packaging",
                                  "Purchase and packaging teams on working with Oxy Pack Global.")
    s = s.replace('<section id="quote" class="sec sec-soft">', home_t + "\n\n" + '<section id="quote" class="sec sec-soft">', 1)
    s = GUIDES_RE.sub("", s)
    if GUIDES:
        assert s.count('<section class="certs"') == 1, "certs section not found"
        s = s.replace('<section class="certs"', home_guides_section() + "\n\n" + '<section class="certs"', 1)
    write("index.html", s)


def write_sitemap():
    today = date.today().isoformat()
    urls = [("", "1.0"), ("products.html", "0.9")] + [(cat_url(c), "0.8") for c in CATEGORIES] + \
           [(prod_url(p), "0.7") for p in PRODUCTS] + [("export.html", "0.9")] + [(market_url(m), "0.8") for m in MARKETS] + [("guides.html", "0.7")] + \
           [(guide_url(g), "0.7") for g in GUIDES] + [("about.html", "0.6"), ("industries.html", "0.6"), ("contact.html", "0.8")]
    body = "\n".join(f"  <url><loc>{SITE}/{u}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>{pr}</priority></url>"
                     for u, pr in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n')


if __name__ == "__main__":
    for c in CATEGORIES:
        build_category(c)
    for p in PRODUCTS:
        build_product(p)
    build_overview()
    build_export()
    for m in MARKETS:
        build_market(m)
    for g in GUIDES:
        build_guide(g)
    build_guides_index()
    update_root_pages()
    update_home()
    write_sitemap()
    print(f"Built products.html, {len(CATEGORIES)} category pages and {len(PRODUCTS)} product pages.")
