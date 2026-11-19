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
HEADER = HEADER.replace(' aria-current="page"', '').replace('<a href="products.html">', '<a href="products.html" aria-current="page">')
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


def page(path, title, desc, main, lds, image="assets/img/og-image.jpg", band=True, extra=""):
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
<meta property="og:type" content="website">
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
    body = HEADER + '\n<main id="main">\n' + main + '\n</main>\n' + band_html + FOOTER + '<script src="assets/js/main.js" defer></script>\n</body>\n</html>\n'
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
    ("Parle", "parle.png", 121, 58), ("Reliance Retail", "reliance-retail.png", 100, 50),
    ("Balaji Wafers", "balaji-wafers.svg", 140, 107), ("Bikaji", "bikaji.png", 134, 73),
    ("Chheda's", "chhedas.png", 296, 120), ("Mother's Recipe", "mothers-recipe.svg", 265, 100),
    ("Gwalia Sweets", "gwalia-sweets.png", 124, 120), ("Ramdev", "ramdev.png", 147, 83),
    ("Vimal Healthy Oils", "vimal.png", 148, 120), ("Kitchen Xpress", "kitchen-xpress.png", 132, 120),
    ("Vijay Mamra", "vijay-mamra.png", 124, 99), ("Shubha", "shubha.png", 400, 84),
    ("Nuvela Pharma", "nuvela-pharma.png", 155, 120), ("Alpha Crop Care", "alpha-crop-care.png", 120, 44),
    ("Primeseal Straps", "primeseal.png", 234, 114), ("Ramoji Foods", None, 0, 0),
    ("Ramraj Namkeen", None, 0, 0), ("Real Bites", None, 0, 0),
]


def client_item(name, f, w, h, hidden=False):
    alt = "" if hidden else e(name)
    if f:
        return f'<img src="assets/img/clients/{f}" alt="{alt}" width="{w}" height="{h}" loading="lazy" decoding="async">'
    return f'<span class="client-name"{" aria-hidden=\"true\"" if hidden else ""}>{e(name)}</span>'


CLIENTS_GRID = ('<!-- clients -->\n<section class="sec clients" aria-labelledby="clients-h">\n<div class="wrap">\n'
                '<div class="sec-head reveal" style="justify-content:center;text-align:center"><div style="max-width:720px">'
                '<p class="eyebrow" style="justify-content:center">Our customers</p>'
                '<h2 class="h2" id="clients-h">Trusted by leading Indian brands</h2>'
                '<p class="lead" style="margin-top:16px">From national FMCG names to regional food, pharma and industrial companies.</p></div></div>\n'
                '<ul class="clients-grid">'
                + "".join(f'<li class="client">{client_item(*c)}</li>' for c in CLIENTS)
                + '</ul>\n</div>\n</section>\n<!-- /clients -->')

_track = "".join(f'<li>{client_item(*c)}</li>' for c in CLIENTS)
_track_dup = "".join(f'<li aria-hidden="true">{client_item(*c, hidden=True)}</li>' for c in CLIENTS)
LOGO_STRIP = ('<!-- clients -->\n<section class="logo-strip" aria-label="Customers">\n'
              '<p class="logo-strip-label">Trusted by leading Indian brands</p>\n'
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
<li><b style="color:#fff">We produce and ship</b> — FOB, CIF or DDP.</li>
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
<p class="lead" style="margin-top:18px">Every item is made to order — your size, board grade and print. Open a product for its specifications and to request a quote.</p>
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

<section class="sec">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Explore more</p><h2 class="h2">Other product categories</h2></div><a href="products.html" class="link-u">All products →</a></div>
<div class="cgrid4">{others}</div>
</div>
</section>'''
    lds = [crumbs_ld(links), ld({"@context": "https://schema.org", "@type": "ItemList", "name": c["name"],
                                 "itemListElement": [{"@type": "ListItem", "position": i, "url": SITE + "/" + prod_url(p), "name": p["name"]}
                                                     for i, p in enumerate(items, 1)]})]
    title = f"{c['name']} | Paper Packaging Exporter | OXY PACK GLOBAL"
    page(cat_url(c), title, f"{c['short']} Made to order in Rajkot, India and exported worldwide by OXY PACK GLOBAL.", main, lds,
         image=c["image"])


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

<section class="sec">
<div class="wrap">
<div class="sec-head"><div><p class="eyebrow">Related products</p><h2 class="h2">You may also need</h2></div><a href="{cat_url(c)}" class="link-u">All {e(c['name'].lower())} →</a></div>
<ul class="pgrid g3c">
{chr(10).join(pcard(x, prod_url(x)) for x in rel)}
</ul>
</div>
</section>'''
    lds = [crumbs_ld(links), ld({"@context": "https://schema.org", "@type": "Product", "name": p["name"],
                                 "description": p["overview"], "image": SITE + "/" + p["img"], "category": c["name"],
                                 "brand": {"@type": "Brand", "name": "OXY PACK GLOBAL"}, "url": SITE + "/" + prod_url(p)})]
    page(prod_url(p), f"{p['name']} | {c['name']} | OXY PACK GLOBAL",
         f"{p['short']} Made to order and exported from India by OXY PACK GLOBAL. HS {p['hs']}.", main, lds,
         image=p["img"], band=False)


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
<li>{TICK}<span>FOB, CIF or DDP shipping to 20+ countries</span></li>
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
    write("index.html", s)


def write_sitemap():
    today = date.today().isoformat()
    urls = [("", "1.0"), ("products.html", "0.9")] + [(cat_url(c), "0.8") for c in CATEGORIES] + \
           [(prod_url(p), "0.7") for p in PRODUCTS] + [("about.html", "0.6"), ("industries.html", "0.6"), ("contact.html", "0.8")]
    body = "\n".join(f"  <url><loc>{SITE}/{u}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>{pr}</priority></url>"
                     for u, pr in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n')


if __name__ == "__main__":
    for c in CATEGORIES:
        build_category(c)
    for p in PRODUCTS:
        build_product(p)
    build_overview()
    update_root_pages()
    update_home()
    write_sitemap()
    print(f"Built products.html, {len(CATEGORIES)} category pages and {len(PRODUCTS)} product pages.")
