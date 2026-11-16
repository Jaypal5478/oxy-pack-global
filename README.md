# OXY PACK GLOBAL — Website

Static website (HTML, CSS, JS) for OXY PACK GLOBAL, a paper packaging manufacturer & exporter from Rajkot, India.

## Structure
- `index.html`, `about.html`, `products.html`, `industries.html`, `contact.html`, `404.html`
- `assets/css/style.css` — all styles
- `assets/js/main.js` — mobile menu, scroll animations, quote form
- `assets/img/` — images, logo, Open Graph image
- `sitemap.xml`, `robots.txt`, `site.webmanifest` — SEO files

## Hosting
Hosted on GitHub Pages: https://jaypal5478.github.io/oxy-pack-global/

### Adding a custom domain later
1. Buy the domain (e.g. oxypackglobal.com).
2. GitHub repo → Settings → Pages → Custom domain → enter `www.oxypackglobal.com`.
3. At your domain provider add a CNAME record `www` → `<username>.github.io`, and A records for the root domain to 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153.
4. Tick "Enforce HTTPS".
5. Replace `https://jaypal5478.github.io/oxy-pack-global` with the new domain in all `.html` files, `sitemap.xml` and `robots.txt`.

## Quote form
The form posts to FormSubmit (free) at sales@oxypackglobal.com. The first submission sends an activation email to that inbox — click the link once to start receiving enquiries.
