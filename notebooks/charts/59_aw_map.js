// Country totals, not inferred office/customer coordinates. Boundary data is
// vendored locally; this code only needs Observable Plot and d3 from the widget.
const sales = new Map(markets.map(d => [d.country_code, d]));
const features = world.features.map(f => ({...f, properties: {
  ...f.properties, ...sales.get(f.properties.code)
}}));
return Plot.plot({
  width, height, marginTop: 25, marginBottom: 25,
  projection: {type: "equal-earth", rotate: [0, -8]},
  style: {background: "white", color: "#334155", fontFamily: "Arial, sans-serif", fontSize: "12px"},
  color: {type: "sqrt", scheme: "Blues", domain: [0, Math.max(1, ...markets.map(d => d.net_sales))],
    label: "Net sales · USD", legend: true, marginLeft: 25, marginRight: 25,
    tickFormat: d3.format("$.2s")},
  marks: [
    Plot.geo(features, {fill: "#f1f5f9", stroke: "#cbd5e1", strokeWidth: 0.5}),
    Plot.geo(features.filter(f => sales.has(f.properties.code)), {
      fill: d => d.properties.net_sales, stroke: "#94a3b8", strokeWidth: 0.6,
      title: d => `${d.properties.name}\nNet sales: ${d3.format("$,.0f")(d.properties.net_sales)}\nOrders: ${d3.format(",")(d.properties.orders)}`,
      tip: true
    })
  ]
});
