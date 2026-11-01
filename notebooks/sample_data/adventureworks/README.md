# AdventureWorks report map

`world-110m.geojson` is a reduced copy of Natural Earth's 1:110m admin-0 country
boundaries. Only geometry, the long country name and `ISO_A2_EH` are retained;
Antarctica is excluded. Sales join by ISO country code, never by an inferred
customer coordinate. All business data stays in the local AdventureWorks Parquet
product and is not copied into this directory.

- Source: [Natural Earth vector](https://github.com/nvkelso/natural-earth-vector/blob/ca96624a56bd078437bca8184e78163e5039ad19/geojson/ne_110m_admin_0_countries.geojson)
- Revision: `ca96624a56bd078437bca8184e78163e5039ad19`
- License: [public domain](https://www.naturalearthdata.com/about/terms-of-use/)

The geometry is local. wigglystuff's `ObservablePlot` loads Plot 0.6.17 and d3
from its CDN; the map needs that browser connection on first use. The report's
Evidential tables and queries do not depend on the map loading.
