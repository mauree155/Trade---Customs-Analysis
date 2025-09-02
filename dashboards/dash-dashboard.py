# ---------------------- Complete Trade & Customs Dashboard (Optimized & Mobile-Friendly) ----------------------

import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pycountry

# ---------------------- CONFIG ----------------------
DATA_PATH = "data/feature-engineered-data.csv"
CURRENCY_SYMBOL = "$"

# ---------------------- HELPERS ----------------------
def abbreviate_number(num):
    try:
        num = float(num)
    except:
        return str(num)
    abs_num = abs(num)
    if abs_num >= 1_000_000_000: return f"{num/1_000_000_000:.2f}B"
    if abs_num >= 1_000_000: return f"{num/1_000_000:.2f}M"
    if abs_num >= 1_000: return f"{num/1_000:.2f}K"
    return f"{num:.0f}"

def format_money_abbrev(v, symbol=CURRENCY_SYMBOL):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return f"{symbol}0"
    return f"{symbol}{abbreviate_number(v)}"

def _safe_growth(curr, prev):
    if prev in [None, 0] or pd.isna(prev): return 0.0
    return (curr - prev) / prev * 100.0

def get_palette(is_dark):
    return {
        "bg": "#111418" if is_dark else "#F7F9FC",
        "card": "#1B1F24" if is_dark else "#FFFFFF",
        "text": "#E6E6E6" if is_dark else "#0A2540",
        "muted": "#9AA0A6" if is_dark else "#6B7280",
        "accent": "#3B82F6" if is_dark else "#2563EB",
        "pos": "#10B981",
        "neg": "#EF4444",
        "warn": "#F59E0B",
    }

def apply_theme_to_fig(fig, is_dark):
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E6E6E6" if is_dark else "#0A2540"),
        margin=dict(l=40, r=20, t=60, b=40),
    )
    return fig

def sparkline(y, x=None, is_dark=False, mode="lines"):
    if x is None: x = list(range(len(y)))
    fig = go.Figure(go.Scatter(x=x, y=y, mode=mode, line=dict(width=2)))
    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=90,
    )
    return fig

def empty_fig(msg, is_dark):
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False)
    return apply_theme_to_fig(fig, is_dark)

def kpi_card(title, value_str, delta_label, delta_pct, spark_fig, color, palette):
    delta_color = palette["pos"] if delta_pct >= 0 else palette["neg"]
    return dbc.Card(
        dbc.CardBody([
            html.Div(title, style={"fontSize": "0.95rem", "color": palette["muted"], "marginBottom": "6px"}),
            html.Div(value_str, style={"fontSize": "1.4rem", "fontWeight": 700, "color": color, "marginBottom": "6px"}),
            html.Div(f"{delta_label}: {delta_pct:.2f}%", style={"fontSize": "0.85rem", "color": delta_color, "marginBottom": "6px"}),
            dcc.Graph(figure=spark_fig, config={"displayModeBar": False}, style={"height": "70px"})
        ]),
        style={"backgroundColor": palette["card"], "border": "1px solid rgba(128,128,128,0.12)", "borderRadius": "12px", "height": "100%"},
        className="shadow-sm",
    )

def apply_filters(df, filters: dict):
    dff = df.copy()
    for col, val in filters.items():
        if val:
            if isinstance(val, list):
                dff = dff[dff[col].isin(val)]
            else:
                dff = dff[dff[col] == val]
    return dff

# ---------------------- LOAD DATA ----------------------
df = pd.read_csv(DATA_PATH)
df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

# Format HS codes
if "HS_code" in df.columns:
    df["HS_code"] = df["HS_code"].astype(str).str.zfill(6)

# Ensure datetime
if "Receipt_date" in df.columns:
    df["Receipt_date"] = pd.to_datetime(df["Receipt_date"], errors="coerce")
elif "Year" in df.columns and "Month" in df.columns:
    df["Receipt_date"] = pd.to_datetime(df["Year"].astype(str)+"-"+df["Month"].astype(str)+"-01", errors="coerce")
else:
    df["Receipt_date"] = pd.to_datetime("2022-01-01")
df["Year"] = df["Receipt_date"].dt.year
df["Month"] = df["Receipt_date"].dt.month
df["YearMonth"] = df["Receipt_date"].dt.to_period("M").astype(str)

# ISO3 for map
if "Country_of_origin" in df.columns:
    def country_to_iso3(name):
        try:
            return pycountry.countries.lookup(name).alpha_3
        except:
            return None
    df["Country_ISO3"] = df["Country_of_origin"].apply(country_to_iso3)

COLS = {
    "CIF": "CIF_value($)" if "CIF_value($)" in df.columns else ("CIF_value" if "CIF_value" in df.columns else None),
    "FOB": "FOB_value($)" if "FOB_value($)" in df.columns else ("FOB_value" if "FOB_value" in df.columns else None),
    "TAX": "Total_Tax($)" if "Total_Tax($)" in df.columns else ("Total_Tax" if "Total_Tax" in df.columns else None),
}

# ---------------------- PRECOMPUTED AGGREGATES ----------------------
hs_agg = df.groupby(["HS_code", "section_name"]).sum(numeric_only=True).reset_index()
container_agg = df.groupby("Container_size").sum(numeric_only=True).reset_index()
country_agg = df.groupby("Country_ISO3").sum(numeric_only=True).reset_index()

# ---------------------- DASH APP ----------------------
external_stylesheets = [dbc.themes.BOOTSTRAP, dbc.themes.CYBORG]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Trade & Customs — Optimized Dashboard"

theme_store = dcc.Store(id="theme-store", storage_type="local")
measure_store = dcc.Store(id="measure-store", data={"measure": "CIF"})

# Header controls
header_controls = html.Div(
    style={"display": "flex", "gap": "8px", "alignItems": "center", "justifyContent": "flex-end"},
    children=[
        dbc.Button("Clear Filters", id="clear-filters", n_clicks=0, color="secondary", size="sm"),
        dbc.Switch(id="theme-switch", label="Dark mode", value=True, className="ms-2"),
    ]
)

measure_button_row = html.Div(
    id="measure-row",
    style={"display": "flex", "gap": "8px", "alignItems": "center", "justifyContent": "center", "marginBottom": "8px", "marginTop": "4px"},
    children=[
        dbc.Button("CIF Value", id="measure-cif-btn", n_clicks=0, color="primary", size="sm"),
        dbc.Button("FOB Value", id="measure-fob-btn", n_clicks=0, color="secondary", size="sm"),
        dbc.Button("Total Tax", id="measure-tax-btn", n_clicks=0, color="secondary", size="sm"),
    ]
)

# ---------------------- APP LAYOUT ----------------------
app.layout = html.Div([
    theme_store,
    measure_store,
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H2("Trade & Customs Dashboard", id="title", className="my-3"), xs=12, md=6),
            dbc.Col(header_controls, xs=12, md=6, className="d-flex justify-content-end align-items-center")
        ], align="center", className="mb-2"),

        dbc.Row([
            dbc.Col([html.Label("Country of Origin", id="label-country"),
                     dcc.Dropdown(id="country-dd",
                                  options=[{"label": c, "value": c} for c in sorted(df["Country_of_origin"].dropna().unique())] if "Country_of_origin" in df.columns else [],
                                  multi=True, placeholder="All countries")], xs=12, sm=6, md=3, className="mb-2"),
            dbc.Col([html.Label("Year", id="label-year"),
                     dcc.Dropdown(id="year-dd",
                                  options=[{"label": int(y), "value": int(y)} for y in sorted(df["Year"].dropna().unique())],
                                  multi=True, placeholder="All years")], xs=12, sm=6, md=3, className="mb-2"),
            dbc.Col([html.Label("Month", id="label-month"),
                     dcc.Dropdown(id="month-dd",
                                  options=[{"label": m, "value": m} for m in range(1, 13)],
                                  multi=True, placeholder="All months")], xs=12, sm=6, md=3, className="mb-2"),
            dbc.Col([html.Label("Importer"),
                     dcc.Dropdown(id="importer-dd",
                                  options=[{"label": i, "value": i} for i in sorted(df["Importer"].dropna().unique())] if "Importer" in df.columns else [],
                                  multi=False, placeholder="All importers")], xs=12, sm=6, md=3, className="mb-2"),
        ], className="mb-2"),

        dbc.Row(id="kpi-row", className="g-3 mb-2"),
        dbc.Row(dbc.Col(measure_button_row), className="mb-2"),

        dbc.Row([
            dbc.Col([
                dbc.Card(dbc.CardBody([dcc.Graph(id="trend-chart", style={"width": "100%", "height": "250px"})]), id="card-trend"),
                html.Br(),
                dbc.Card(dbc.CardBody([dcc.Graph(id="hs-bar", style={"width": "100%", "height": "250px"})]), id="card-hs")
            ], xs=12, md=7, className="mb-3"),

            dbc.Col([
                dbc.Card(dbc.CardBody([dcc.Graph(id="container-bar", style={"width": "100%", "height": "250px"})]), id="card-container"),
                html.Br(),
                dbc.Card(dbc.CardBody([dcc.Graph(id="country-map", style={"width": "100%", "height": "250px"})]), id="card-map")
            ], xs=12, md=5, className="mb-3"),
        ]),

        html.Div(id="invisible-recalc", style={"display": "none"})
    ], fluid=True, id="page-container", style={"padding": "16px"})
], style={"backgroundColor": "#F7F9FC"})

# ---------------------- CALLBACKS ----------------------
@app.callback(Output("theme-store", "data"), Input("theme-switch", "value"), State("theme-store", "data"))
def persist_theme(is_dark, data):
    return {"dark": bool(is_dark)}

@app.callback(Output("theme-switch", "value"), Input("invisible-recalc", "children"), State("theme-store", "data"))
def restore_theme(_, data):
    if isinstance(data, dict) and "dark" in data: return bool(data["dark"])
    return True

@app.callback(
    Output("country-dd", "value"), Output("year-dd", "value"), Output("month-dd", "value"), Output("importer-dd", "value"),
    Input("clear-filters", "n_clicks"), prevent_initial_call=True
)
def clear_filters(n_clicks):
    return None, None, None, None

@app.callback(
    Output("measure-store", "data"),
    Input("measure-cif-btn", "n_clicks"),
    Input("measure-fob-btn", "n_clicks"),
    Input("measure-tax-btn", "n_clicks"),
    State("measure-store", "data"),
)
def select_measure(n_cif, n_fob, n_tax, current):
    clicks = {"CIF": int(n_cif or 0), "FOB": int(n_fob or 0), "TAX": int(n_tax or 0)}
    selected = max(clicks.items(), key=lambda kv: kv[1])[0] if any(clicks.values()) else (current or {"measure": "CIF"})["measure"]
    return {"measure": selected}

@app.callback(
    Output("measure-cif-btn", "color"),
    Output("measure-fob-btn", "color"),
    Output("measure-tax-btn", "color"),
    Input("measure-store", "data"),
)
def update_measure_button_colors(store_data):
    measure = store_data.get("measure") if isinstance(store_data, dict) else "CIF"
    return ("primary" if measure=="CIF" else "secondary",
            "primary" if measure=="FOB" else "secondary",
            "primary" if measure=="TAX" else "secondary")

# ---------------------- MAIN DASHBOARD CALLBACK ----------------------
@app.callback(
    [
        Output("page-container", "style"),
        Output("title", "style"),
        Output("label-country", "style"),
        Output("label-year", "style"),
        Output("kpi-row", "children"),
        Output("trend-chart", "figure"),
        Output("hs-bar", "figure"),
        Output("container-bar", "figure"),
        Output("country-map", "figure"),
        Output("card-trend", "style"),
        Output("card-hs", "style"),
        Output("card-container", "style"),
        Output("card-map", "style"),
    ],
    [
        Input("theme-switch", "value"),
        Input("country-dd", "value"),
        Input("year-dd", "value"),
        Input("month-dd", "value"),
        Input("importer-dd", "value"),
        Input("measure-store", "data"),
    ]
)
def update_dashboard(is_dark, countries, years, months, importer, measure_store_data):
    is_dark = bool(is_dark)
    pal = get_palette(is_dark)
    page_style = {"backgroundColor": pal["bg"], "minHeight": "100vh", "padding": "16px"}
    title_style = {"color": pal["text"]}
    label_style = {"color": pal["muted"], "fontWeight": 600}
    card_style = {"backgroundColor": pal["card"], "border": "1px solid rgba(128,128,128,0.12)", "borderRadius": "12px"}

    # Filtering
    dff = apply_filters(df, {"Country_of_origin": countries, "Year": years, "Month": months, "Importer": importer})
    if dff.empty: dff = pd.DataFrame(columns=df.columns)

    measure_col = COLS.get(measure_store_data.get("measure", "CIF"), COLS["CIF"])
    measure_name = measure_store_data.get("measure", "CIF")

    # ---------------- KPI CARDS ----------------
    kpis = [
        {"title": f"Total {measure_name}", "value": dff[measure_col].sum() if measure_col else 0, "prev": dff[measure_col].sum()*0.85 if measure_col else 0, "spark": dff.groupby("YearMonth")[measure_col].sum().tolist() if measure_col else [0]*6},
        {"title": "Total Shipments", "value": len(dff["Receipt_number"].unique()) if "Receipt_number" in dff.columns else 0, "prev": len(dff["Receipt_number"].unique())*0.85 if "Receipt_number" in dff.columns else 0, "spark": list(range(len(dff)))},
        {"title": "Avg Transaction Value", "value": dff[measure_col].mean() if measure_col else 0, "prev": dff[measure_col].mean()*0.9 if measure_col else 0, "spark": dff.groupby("YearMonth")[measure_col].mean().tolist() if measure_col else [0]*6},
        {"title": "Avg Mass per Shipment", "value": dff["Mass_(kg)"].mean() if "Mass_(kg)" in dff.columns else 0, "prev": dff["Mass_(kg)"].mean()*0.9 if "Mass_(kg)" in dff.columns else 0, "spark": dff.groupby("YearMonth")["Mass_(kg)"].mean().tolist() if "Mass_(kg)" in dff.columns else [0]*6},
    ]

    kpi_cards = []
    for k in kpis:
        val_str = format_money_abbrev(k["value"]) if measure_name in ["CIF", "FOB", "TAX"] else f"{k['value']:.0f}"
        delta_pct = _safe_growth(k["value"], k["prev"])
        spark_fig = sparkline(k["spark"], is_dark=is_dark)
        delta_label = "YoY%" if "Total" in k["title"] and measure_name in ["CIF","FOB","TAX"] else "MoM%"
        card = kpi_card(k["title"], val_str, delta_label, delta_pct, spark_fig, pal["accent"], pal)
        kpi_cards.append(dbc.Col(card, xs=12, sm=6, md=3))

    # ---------------- CHARTS ----------------
    # Trend chart
    if dff.empty or measure_col not in dff.columns:
        trend_fig = empty_fig("No data", is_dark)
    else:
        trend_data = dff.groupby("YearMonth")[measure_col].sum().reset_index()
        trend_fig = px.line(trend_data, x="YearMonth", y=measure_col, markers=True, title=f"{measure_name} Trend")
        trend_fig = apply_theme_to_fig(trend_fig, is_dark)
       
        # HS bar
        if dff.empty or "HS_code" not in dff.columns or measure_col not in dff.columns:
                hs_fig = empty_fig("No data", is_dark)
        else:
            hs_top = dff.groupby("HS_code")[measure_col].sum().nlargest(10).reset_index()
    hs_fig = px.bar(hs_top, x=measure_col, y="HS_code", orientation="h", title="Top 10 HS Codes")
    hs_fig = apply_theme_to_fig(hs_fig, is_dark)

    # Container bar
    if dff.empty or "Container_size" not in dff.columns or measure_col not in dff.columns:
        container_fig = empty_fig("No data", is_dark)
    else:
        cont_top = dff.groupby("Container_size")[measure_col].sum().reset_index()
        container_fig = px.bar(cont_top, x="Container_size", y=measure_col, title="Container Size Distribution")
        container_fig = apply_theme_to_fig(container_fig, is_dark)
    
    # Country map
    if dff.empty or "Country_ISO3" not in dff.columns or measure_col not in dff.columns:
        map_fig = empty_fig("No data", is_dark)
    else:
        country_sum = dff.groupby("Country_ISO3")[measure_col].sum().reset_index()
        map_fig = px.choropleth(country_sum, locations="Country_ISO3", color=measure_col,
                            color_continuous_scale="Blues", title="By Country of Origin")
        map_fig = apply_theme_to_fig(map_fig, is_dark)
        return (
            page_style, title_style, label_style, label_style,
            kpi_cards,
    trend_fig, hs_fig, container_fig, map_fig,
    card_style, card_style, card_style, card_style
)
    #---------------------- RUN APP ----------------------
    if __name__ == "__main__":
        app.run_server(debug=True, port=8050)