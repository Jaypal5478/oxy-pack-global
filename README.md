# OXY PACK GLOBAL — Website

Static website (HTML, CSS, JS) for OXY PACK GLOBAL, a paper packaging manufacturer & exporter from Rajkot, India.

## Structure
- `index.html`, `about.html`, `products.html`, `industries.html`, `contact.html`, `404.html`
- `products/` — 5 category pages and 20 product pages (generated, don't edit by hand)
- `export.html`, `guides.html`, `guides/` — export page, buyer guides index and guide articles (generated)
- `tools/products_data.py` — text, specs and images for every category and product
- `tools/guides_data.py` — buyer guide articles (title, meta description, body HTML, FAQs, related products)
- `tools/build_products.py` — rebuilds `products.html`, `products/`, the home-page product tiles and quote form, footer product links and `sitemap.xml`. After editing the data (or the header/footer in `about.html`), run `python tools/build_products.py`
- `assets/css/style.css` — all styles
- `assets/js/main.js` — mobile menu, scroll animations, quote form
- `assets/img/` — images, logo, Open Graph image
- `sitemap.xml`, `robots.txt`, `site.webmanifest` — SEO files

## Hosting
Hosted on GitHub Pages with the custom domain https://oxypackglobal.com (see `CNAME`). Canonical URLs, Open Graph tags, `sitemap.xml` and `robots.txt` all use this domain; `SITE` in `tools/build_products.py` sets it for generated pages.

### Adding a custom domain later
1. Buy the domain (e.g. oxypackglobal.com).
2. GitHub repo → Settings → Pages → Custom domain → enter `www.oxypackglobal.com`.
3. At your domain provider add a CNAME record `www` → `<username>.github.io`, and A records for the root domain to 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153.
4. Tick "Enforce HTTPS".
5. Replace `https://jaypal5478.github.io/oxy-pack-global` with the new domain in all `.html` files, `sitemap.xml` and `robots.txt`.

## Photo credits
- Paper carry bags photo: "Bolsas de asa plana" by Bolsapubli, CC BY-SA 3.0, via Wikimedia Commons (https://commons.wikimedia.org/wiki/File:Bolsas-de-asa-plana-interior-bolsapubli.jpg). Replace with your own product photos when available.
- Customer logos in `assets/img/clients/`: taken from each customer's own website and shown with their agreement as customers. The list and order are in `CLIENTS` in `tools/build_products.py`.
- Product photos in `assets/img/products/`: Pexels (free licence, https://www.pexels.com/license/). Replace a photo by saving your own 4:3 image over the same file name.

## Quote form
The form posts to FormSubmit (free) at sales@oxypackglobal.com. The first submission sends an activation email to that inbox — click the link once to start receiving enquiries.
