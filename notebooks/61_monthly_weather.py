# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo", "evidential"]
# ///
"""Historical monthly weather: rounded intervals on a common temperature gradient."""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")


@app.cell
def imports():
    import json

    import marimo as mo

    from evidential import EvidentialTable, col, settings

    return EvidentialTable, col, json, mo, settings


@app.cell(hide_code=True)
def introduction(mo):
    mo.md("""
    # A year of weather, city by city

    Choose one of ten US cities. Each row covers a month between **July 2014 and
    June 2015**. The rounded range shows the coldest and hottest daily readings
    recorded that month; the two smaller dots show its **average daily low and
    high**. Hover to inspect the numbers. Rain is the month's total precipitation,
    expressed as its liquid equivalent.

    Colours are anchored to a fixed **−30 to 50°C** scale across every city and
    month: cold temperatures are blue, mild temperatures green and hot ones gold
    through orange. The faint track shows that common domain. Switching cities
    changes the data in the existing widget, preserving its column configuration.
    These are historical observations, not forecasts or climate normals.

    ```python
    col.range("low", "high", cap="round", size=8).gradient(
        scale=["#537bc4", "#67c9d4", "#add5ae", "#ffe04b", "#ef893c"],
        min=-30, max=50,
    ).scale(domain=(-30, 50))
    ```

    Source: [Weather Underground, via FiveThirtyEight's US Weather History](https://github.com/fivethirtyeight/data/tree/master/us-weather-history),
    CC BY 4.0. A committed monthly aggregation of the local `~/datasets/`
    copy makes the notebook usable offline. Airport/central-city stations differ;
    observations describe those stations rather than an entire metropolitan area.
    """)
    return


@app.cell
def dataset(json, mo):
    weather_rows = json.loads(
        (mo.notebook_location() / "data" / "61_monthly_weather_2014_15.json").read_text()
    )
    cities = sorted({row["city"] for row in weather_rows})
    return cities, weather_rows


@app.cell
def city_control(cities, mo):
    city_picker = mo.ui.dropdown(options=cities, value="New York", label="City")
    city_picker
    return (city_picker,)


@app.cell
def weather_table(EvidentialTable, col, mo, settings):
    monthly_weather = mo.ui.anywidget(
        EvidentialTable(
            [],
            columns=[
                col.text("period", title="Month", align='right'),
                col.number("low", title="Lowest", format='0.0"°C"'),
                col.range(lambda row: -30, lambda row: 50, cap="round", size=8, color="#e2e8f0")
                   .range("low", "high", cap="round", size=8)
                   .gradient(scale=["#537bc4", "#67c9d4", "#add5ae", "#ffe04b", "#ef893c"], min=-30, max=50)
                   .point("avg_low", color="#00000000", outline="#475569", size=8)
                   .point("avg_high", color="#00000000", outline="#475569", size=8)
                   .title("Temperature").fmt('0.0"°C"')
                   .scale(domain=(-30, 50), axis=True, axis_position="bottom"),
                col.number("high", title="Highest", format='0.0"°C"'),
                col.number("rain_mm", title="Rain (mm)", format="num1"),
            ],
            settings=settings(border=False, row_lines=False, row_shading=3, page_size=0, search=False, width=780),
        )
    )
    monthly_weather
    return (monthly_weather,)


@app.cell
def update_weather(city_picker, monthly_weather, weather_rows):
    city_months = [row for row in weather_rows if row["city"] == city_picker.value]
    with monthly_weather.widget.hold_sync():
        monthly_weather.widget.set_data(city_months)
        monthly_weather.widget.update_options(
            title=f"{city_picker.value} · a year of weather",
            subtitle="July 2014–June 2015 · monthly extremes, with average daily low/high marked in white",
            caption=f"Station {city_months[0]['station']} · Weather Underground / FiveThirtyEight · CC BY 4.0. "
            "All temperatures in °C; precipitation converted from inches to mm.",
        )
    return


if __name__ == "__main__":
    app.run()
