---
layout: ../layouts/BaseLayout.astro
title: About
---

# About

**Local Boundaries** is a project by [Open Knowledge Nepal](https://oknp.org) that publishes the administrative
boundary geodata of Nepal — provinces, districts, and local levels — as free, open, and reusable data, in
whichever format your tools expect: GeoJSON, TopoJSON, Shapefile, KML, or GeoPackage.

Following the Constitution of Nepal (2015), the country was restructured into 7 provinces and local levels
categorized as rural municipality, municipality, metropolitan city, and sub-metropolitan city. Prior to this
project, up-to-date digital boundary files for these units were difficult for developers, researchers, and
civic-tech projects to find in an open format. Local Boundaries fills that gap.

Explore the data on the [interactive map](/map/), or head straight to the
[download catalog](/download/) for whole-country or per-province files.

## What's included
* Provinces (7)
* Districts (77) — dissolved from local-level boundaries by district, since no separately-attributed district
  source exists
* Local levels: Rural Municipality (Gaupalika), Municipality (Nagarpalika), Metropolitan City
  (Mahanagarpalika), Sub-Metropolitan City (Upamahanagarpalika)
* National parks, wildlife reserves, hunting reserves, and other protected/special areas

## Other Nepal GIS data sources
Local Boundaries focuses on administrative boundaries. For other kinds of geospatial data, see:
* [Survey Department / National Geoportal](https://nationalgeoportal.gov.np/) — official topographic and
  administrative data
* [Department of Land Information and Archive](http://dolia.gov.np) — cadastral (parcel-level) data
* [Humanitarian Data Exchange](https://data.humdata.org/group/npl) — humanitarian and crowdsourced datasets
* [OpenStreetMap](https://www.openstreetmap.org/) — crowdsourced, continuously updated map data

## License
The datasets are licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
You are free to use, share, and adapt this data for any purpose, including commercially, as long as you give
appropriate credit.

## Contributing
Found an error in the boundary data, or have an update to suggest? Open an issue or pull request on
[GitHub](https://github.com/openknowledgenp/localboundaries). The data pipeline that generates every downloadable file
from source is in `scripts/generate_datasets.py`.
