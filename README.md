# Local Boundaries

Open, reusable administrative boundary data for Nepal's provinces, districts, and local levels, published as
GeoJSON, TopoJSON, Shapefile, KML, and GeoPackage — whole-country or split per province.

Published at: https://localboundries.oknp.org

## Levels included
* Provinces (7)
* Districts (77) — dissolved from local-level boundaries by district
* Local levels: Rural Municipality (Gaupalika), Municipality (Nagarpalika), Metropolitan City (Mahanagarpalika),
  Sub-Metropolitan City (Upamahanagarpalika)
* National parks, wildlife reserves, hunting reserves, and other protected/special areas

## Site

The site is a static [Astro](https://astro.build) app.

```
npm install
npm run dev       # local dev server
npm run build     # build to dist/
npm run preview   # preview the production build
```

Deployment is automatic via `.github/workflows/deploy.yml` on every push to `gh-pages`.

## Data pipeline

Every downloadable file under `public/data/` is generated from the source GeoJSON in `source/` by
`scripts/generate_datasets.py`:

```
pip install -r scripts/requirements.txt
python3 scripts/generate_datasets.py
```

This regenerates `public/data/`, `src/data/datasets.json` (the download catalog manifest), and
`src/data/stats.json` (the homepage stat tiles).

## License
The datasets are licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
