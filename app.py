import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kastoria · Color Intelligence",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

/* ── root & body ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #0d0f14;
    color: #e8eaf0;
}

/* ── hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1400px; }

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: #12151c !important;
    border-right: 1px solid #1e2330;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown p { color: #e8eaf0; }
[data-testid="stSidebarContent"] { padding: 2rem 1.2rem; }

/* ── app header ── */
.app-header {
    background: linear-gradient(135deg, #0d0f14 0%, #111827 50%, #0d0f14 100%);
    border-bottom: 1px solid #1e2330;
    padding: 2rem 0 1.6rem;
    margin-bottom: 2rem;
}
.app-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, #64b5f6, #4dd0e1, #80cbc4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.1;
}
.app-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    color: #6b7280;
    margin-top: 0.4rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── metric cards ── */
.metric-grid { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
.metric-card {
    background: #12151c;
    border: 1px solid #1e2330;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    flex: 1;
    min-width: 160px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #64b5f6, #4dd0e1);
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #e8eaf0;
    line-height: 1;
}
.metric-label {
    font-size: 0.75rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
}

/* ── section headers ── */
.section-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #4dd0e1;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 2rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1e2330, transparent);
    margin-left: 0.5rem;
}

/* ── chart cards ── */
.chart-card {
    background: #12151c;
    border: 1px solid #1e2330;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #12151c;
    border-radius: 12px;
    padding: 4px;
    gap: 2px;
    border: 1px solid #1e2330;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    color: #6b7280;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    padding: 0.6rem 1.4rem;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1a2744, #162535) !important;
    color: #4dd0e1 !important;
    border: 1px solid #1e3a5f !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.5rem;
}

/* ── select/radio widgets ── */
.stRadio > div { gap: 0.5rem; }
.stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 0.85rem;
    color: #9ca3af;
}
.stSelectbox label, .stRadio label, .stSlider label {
    color: #9ca3af !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── divider ── */
hr { border-color: #1e2330; margin: 1.5rem 0; }

/* ── color swatches in table ── */
.color-dot {
    display: inline-block;
    width: 12px; height: 12px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}

/* ── scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY THEME ─────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(18,21,28,1)",
    font=dict(family="Inter, sans-serif", color="#9ca3af", size=12),
    xaxis=dict(gridcolor="#1e2330", zerolinecolor="#1e2330", linecolor="#1e2330"),
    yaxis=dict(gridcolor="#1e2330", zerolinecolor="#1e2330", linecolor="#1e2330"),
    margin=dict(l=12, r=12, t=40, b=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    coloraxis_colorbar=dict(tickfont=dict(color="#9ca3af")),
)
ACCENT = ["#64b5f6","#4dd0e1","#80cbc4","#a5d6a7","#fff176",
          "#ffb74d","#ef9a9a","#ce93d8","#f48fb1","#80deea"]

# ─── DATA LOADER ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    path = "color_summary_batch.xlsx"

    # Summary
    df_sum = pd.read_excel(path, sheet_name="Summary", header=2)
    df_sum.columns = ["#","URL","Filename","ID","Monument","WxH",
                      "R_mean","G_mean","B_mean","H_mean","S_mean","V_mean",
                      "L_mean","C_mean",
                      "C1_hex","C1_pct","C1_name",
                      "C2_hex","C2_pct","C2_name",
                      "C3_hex","C3_pct","C3_name",
                      "C4_hex","C4_pct","C4_name",
                      "C5_hex","C5_pct","C5_name","Status"]
    df_sum = df_sum.dropna(subset=["Monument"])
    for c in ["R_mean","G_mean","B_mean","H_mean","S_mean","V_mean",
              "L_mean","C_mean","C1_pct","C2_pct","C3_pct","C4_pct","C5_pct"]:
        df_sum[c] = pd.to_numeric(df_sum[c], errors="coerce")
    df_sum["#"] = pd.to_numeric(df_sum["#"], errors="coerce")
    df_sum = df_sum.dropna(subset=["#"])

    # Clusters
    df_cl_raw = pd.read_excel(path, sheet_name="Clusters", header=0)
    df_cl_raw.columns = df_cl_raw.iloc[0]
    df_cl = df_cl_raw.iloc[1:].reset_index(drop=True)
    df_cl.columns = ["#","URL","Filename","Cluster","Pixels","Pct","HEX",
                     "Swatch","R","G","B","H","S","V","L","a","b","Name"]
    for c in ["#","Pixels","Pct","R","G","B","H","S","V","L","a","b"]:
        df_cl[c] = pd.to_numeric(df_cl[c], errors="coerce")
    df_cl = df_cl.dropna(subset=["#"])
    # Join monument from summary
    mon_map = df_sum[["#","Monument"]].drop_duplicates("#")
    df_cl = df_cl.merge(mon_map, on="#", how="left")

    # Statistics
    df_stat = pd.read_excel(path, sheet_name="Statistics", header=2)
    df_stat.columns = ["#","URL","Filename","Space","Channel",
                       "Mean","Median","Min","Max","Std","_1","_2","_3"]
    for c in ["#","Mean","Median","Min","Max","Std"]:
        df_stat[c] = pd.to_numeric(df_stat[c], errors="coerce")
    df_stat = df_stat.dropna(subset=["Space","Channel"])
    df_stat = df_stat.merge(mon_map, on="#", how="left")

    return df_sum, df_cl, df_stat


# ─── LONG-FORMAT COLORS ───────────────────────────────────────────────────────
@st.cache_data
def melt_colors(df_sum):
    frames = []
    for i in range(1, 6):
        suffix = "" if i == 1 else f".{i-1}"
        tmp = df_sum[["#","Monument",f"C{i}_hex",f"C{i}_pct",f"C{i}_name"]].copy()
        tmp.columns = ["#","Monument","HEX","Pct","Name"]
        tmp["Rank"] = i
        frames.append(tmp)
    df = pd.concat(frames, ignore_index=True)
    df = df.dropna(subset=["Name","Pct"])
    df["Name"] = df["Name"].str.strip()
    return df


# ─── LOAD ─────────────────────────────────────────────────────────────────────
with st.spinner("Loading color intelligence data…"):
    df_sum, df_cl, df_stat = load_data()
    df_long = melt_colors(df_sum)

monuments = sorted(df_sum["Monument"].dropna().unique())

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <p class="app-title">Kastoria · Color Intelligence</p>
  <p class="app-subtitle">TripAdvisor Visitor Photo Analysis · Color Profiling System</p>
</div>
""", unsafe_allow_html=True)

# ─── KPI CARDS ────────────────────────────────────────────────────────────────
n_images   = int(df_sum["#"].nunique())
n_places   = int(df_sum["Monument"].nunique())
n_clusters = int(df_cl.shape[0])
n_colors   = int(df_long["Name"].nunique())

st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-value">{n_images:,}</div>
    <div class="metric-label">Images Analyzed</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">{n_places}</div>
    <div class="metric-label">Monuments / POIs</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">{n_clusters:,}</div>
    <div class="metric-label">Color Clusters</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">{n_colors}</div>
    <div class="metric-label">Unique Color Names</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎛 Filters")
    st.markdown("---")

    sel_monuments = st.multiselect(
        "Monuments / POIs",
        options=monuments,
        default=monuments,
        help="Filter all charts by selected locations"
    )
    if not sel_monuments:
        sel_monuments = monuments

    st.markdown("---")
    st.markdown("### 🗃 Data File")
    st.code("color_summary_batch.xlsx", language=None)
    st.caption("Place in repo root on GitHub → deploy via Streamlit Cloud.")

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem;color:#4b5563;line-height:1.7">
    Built with <strong style="color:#4dd0e1">Streamlit</strong> · Plotly<br>
    Data: TripAdvisor · Kastoria, Greece<br>
    Color extraction: Image Color Summarizer
    </div>
    """, unsafe_allow_html=True)

# ─── FILTERED DATA ────────────────────────────────────────────────────────────
df_f    = df_sum[df_sum["Monument"].isin(sel_monuments)]
df_lf   = df_long[df_long["Monument"].isin(sel_monuments)]
df_clf  = df_cl[df_cl["Monument"].isin(sel_monuments)]
df_stf  = df_stat[df_stat["Monument"].isin(sel_monuments)]

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab_sum, tab_cl, tab_stat = st.tabs(["🎨  Summary", "🔵  Clusters", "📊  Statistics"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 · SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
with tab_sum:

    # ── 1. Color Frequency Bar Chart ─────────────────────────────────────────
    st.markdown('<div class="section-header">Color Frequency</div>', unsafe_allow_html=True)

    view_mode = st.radio(
        "View mode",
        ["🌐  Top 10 Colors — Overall", "📍  Top 5 Colors — per Monument"],
        horizontal=True,
        key="bar_mode"
    )

    if "Overall" in view_mode:
        agg = (df_lf.groupby("Name")["Pct"].mean()
                    .sort_values(ascending=False).head(10).reset_index())
        # Assign color per name
        hex_map = df_lf.groupby("Name")["HEX"].first().to_dict()
        agg["color"] = agg["Name"].map(hex_map).fillna("#4dd0e1")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=agg["Pct"], y=agg["Name"],
            orientation="h",
            marker=dict(color=agg["color"].tolist(), line=dict(width=0)),
            text=agg["Pct"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(color="#9ca3af", size=11),
        ))
        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text="Top 10 Dominant Colors · Avg Coverage %",
                       font=dict(color="#e8eaf0", size=14, family="Syne, sans-serif")),
            yaxis=dict(autorange="reversed", gridcolor="#1e2330", linecolor="#1e2330",
                       tickfont=dict(color="#c9d1d9")),
            xaxis=dict(title="Avg % Coverage", gridcolor="#1e2330", linecolor="#1e2330"),
            height=420,
        )
    else:
        sel_mon = st.selectbox("Select Monument", sel_monuments, key="bar_mon")
        agg = (df_lf[df_lf["Monument"] == sel_mon]
               .groupby("Name")["Pct"].mean()
               .sort_values(ascending=False).head(5).reset_index())
        hex_map = df_lf.groupby("Name")["HEX"].first().to_dict()
        agg["color"] = agg["Name"].map(hex_map).fillna("#4dd0e1")
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=agg["Pct"], y=agg["Name"],
            orientation="h",
            marker=dict(color=agg["color"].tolist(), line=dict(width=0)),
            text=agg["Pct"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(color="#9ca3af", size=11),
        ))
        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text=f"Top 5 Colors · {sel_mon}",
                       font=dict(color="#e8eaf0", size=14, family="Syne, sans-serif")),
            yaxis=dict(autorange="reversed", gridcolor="#1e2330", linecolor="#1e2330",
                       tickfont=dict(color="#c9d1d9")),
            xaxis=dict(title="Avg % Coverage", gridcolor="#1e2330", linecolor="#1e2330"),
            height=320,
        )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ── 2. Pie Chart + Heatmap side by side ──────────────────────────────────
    col_pie, col_heat = st.columns([1, 1.6], gap="large")

    with col_pie:
        st.markdown('<div class="section-header">Dominant Colors</div>',
                    unsafe_allow_html=True)
        # Only rank-1 colors (dominant per image)
        dom = (df_lf[df_lf["Rank"] == 1].groupby("Name")["Pct"].mean()
               .sort_values(ascending=False).head(12).reset_index())
        hex_map = df_lf.groupby("Name")["HEX"].first().to_dict()
        dom["color"] = dom["Name"].map(hex_map).fillna("#4dd0e1")

        fig_pie = go.Figure(go.Pie(
            labels=dom["Name"],
            values=dom["Pct"],
            hole=0.52,
            marker=dict(colors=dom["color"].tolist(),
                        line=dict(color="#0d0f14", width=2)),
            textinfo="label+percent",
            textfont=dict(size=10, color="#e8eaf0"),
            hovertemplate="<b>%{label}</b><br>Avg: %{value:.1f}%<extra></extra>",
        ))
        fig_pie.add_annotation(
            text=f"<b>{n_images}</b><br><span style='font-size:10px'>images</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#e8eaf0", family="Syne, sans-serif"),
            align="center"
        )
        fig_pie.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text="Dominant Color Share",
                       font=dict(color="#e8eaf0", size=14, family="Syne, sans-serif")),
            showlegend=False,
            height=400,
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_heat:
        st.markdown('<div class="section-header">Color Intensity Heatmap</div>',
                    unsafe_allow_html=True)

        # Pivot: Monument × Color Name, values = mean Pct
        top_colors = (df_lf.groupby("Name")["Pct"].mean()
                      .sort_values(ascending=False).head(12).index.tolist())
        df_heat_base = df_lf[df_lf["Name"].isin(top_colors)]
        pivot = (df_heat_base.groupby(["Monument","Name"])["Pct"]
                 .mean().unstack(fill_value=0))
        # reorder columns by overall frequency
        pivot = pivot.reindex(columns=[c for c in top_colors if c in pivot.columns])
        # Shorten monument names
        short = {m: m.replace("Cave of Dragon (Spilia tou drakou)", "Dragon Cave")
                      .replace("Church of St. Taksiarkhov u Mitropolii", "St. Taksiarhov")
                      .replace("Church of the Panagia Koumbelidiki", "Koumbelidiki")
                      .replace("Culture 8 Cultural City and Nature Guided Day Tours", "Culture 8")
                      .replace("Kastorian Byzantine Churches.", "Byzantine Ch.")
                      .replace("Panagia Mavriotissa Monastery", "Mavriotissa")
                      .replace("Wax Museum  of Mavrochoriou Kastorias", "Wax Museum")
                      .replace("Byzantine Museum of Kastoria", "Byzantine Museum")
                      for m in pivot.index}
        pivot.index = [short.get(m, m) for m in pivot.index]
        pivot = pivot[pivot.index.isin([short.get(m, m) for m in sel_monuments])]

        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[
                [0.0,  "#0d0f14"],
                [0.2,  "#0e2a3a"],
                [0.4,  "#0f4c64"],
                [0.6,  "#1a7a9e"],
                [0.8,  "#3db8d8"],
                [1.0,  "#80deea"],
            ],
            hoverongaps=False,
            hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Avg coverage: %{z:.1f}%<extra></extra>",
            xgap=2, ygap=2,
        ))
        fig_heat.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text="Monuments × Color Name · Avg Coverage %",
                       font=dict(color="#e8eaf0", size=14, family="Syne, sans-serif")),
            xaxis=dict(tickangle=-35, tickfont=dict(size=10, color="#9ca3af"),
                       side="bottom", gridcolor="rgba(0,0,0,0)"),
            yaxis=dict(tickfont=dict(size=10, color="#9ca3af"), autorange="reversed",
                       gridcolor="rgba(0,0,0,0)"),
            height=400,
            margin=dict(l=10, r=20, t=40, b=80),
        )
        st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 · CLUSTERS
# ══════════════════════════════════════════════════════════════════════════════
with tab_cl:

    # ── Scatter: Brightness vs Saturation ────────────────────────────────────
    st.markdown('<div class="section-header">Brightness vs Saturation</div>',
                unsafe_allow_html=True)

    df_scatter = df_clf.dropna(subset=["S","V","HEX","Monument"])

    col_s1, col_s2 = st.columns([3, 1])
    with col_s2:
        sample_n = st.slider("Max points", 500, min(8000, len(df_scatter)),
                             min(3000, len(df_scatter)), 500, key="scatter_n")
        color_by = st.selectbox("Color by", ["Monument","Color Name","HEX"],
                                key="scatter_col")

    df_samp = df_scatter.sample(n=min(sample_n, len(df_scatter)), random_state=42)

    if color_by == "Monument":
        col_field = "Monument"
        col_seq = ACCENT
    elif color_by == "Color Name":
        col_field = "Name"
        col_seq = ACCENT
    else:
        col_field = None  # use actual hex

    if col_field:
        fig_sc = px.scatter(
            df_samp, x="S", y="V",
            color=col_field,
            color_discrete_sequence=col_seq,
            opacity=0.7,
            labels={"S": "Saturation %", "V": "Brightness (Value) %", col_field: col_field},
            hover_data={"HEX": True, "Name": True, "Pct": True},
        )
    else:
        fig_sc = go.Figure(go.Scatter(
            x=df_samp["S"], y=df_samp["V"],
            mode="markers",
            marker=dict(
                color=df_samp["HEX"].tolist(),
                size=5, opacity=0.75,
                line=dict(width=0)
            ),
            text=df_samp["Name"],
            hovertemplate="<b>%{text}</b><br>S: %{x:.1f}%  V: %{y:.1f}%<extra></extra>",
        ))

    fig_sc.update_traces(marker=dict(size=5))
    fig_sc.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Color Cluster Points · Saturation vs Brightness",
                   font=dict(color="#e8eaf0", size=14, family="Syne, sans-serif")),
        xaxis=dict(title="Saturation %", gridcolor="#1e2330", linecolor="#1e2330",
                   range=[-2, 102]),
        yaxis=dict(title="Brightness %", gridcolor="#1e2330", linecolor="#1e2330",
                   range=[-2, 102]),
        height=460,
        legend=dict(font=dict(size=10), itemsizing="constant"),
    )
    with col_s1:
        st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown("---")

    # ── Cluster Visualization ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">Color Profile Clusters · per Monument</div>',
                unsafe_allow_html=True)

    st.caption("Each bubble = one color cluster. Size = pixel coverage %. "
               "Position = mean brightness × saturation centroid per monument.")

    # Aggregate clusters per monument
    agg_cl = (df_clf.groupby(["Monument","Name"])
              .agg(Pct=("Pct","mean"), V=("V","mean"), S=("S","mean"),
                   H=("H","mean"), Count=("Pct","count"))
              .reset_index())
    agg_cl = agg_cl[agg_cl["Pct"] > 1.5].dropna()

    # build hex from HSV mean
    def hsv_to_hex(h, s, v):
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h/360, s/100, v/100)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    agg_cl["color"] = agg_cl.apply(
        lambda r: hsv_to_hex(r["H"], r["S"], r["V"]), axis=1)

    fig_bub = px.scatter(
        agg_cl, x="S", y="V",
        size="Pct", color="Monument",
        color_discrete_sequence=ACCENT,
        text="Name",
        size_max=50,
        labels={"S":"Saturation %","V":"Brightness %","Pct":"Coverage %"},
        hover_data={"Monument": True,"Name": True,"Pct":":.1f","S":":.0f","V":":.0f"},
    )
    fig_bub.update_traces(textfont=dict(size=9, color="rgba(255,255,255,0.6)"),
                          textposition="top center")
    fig_bub.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Aggregated Color Clusters · Bubble = Avg Coverage",
                   font=dict(color="#e8eaf0", size=14, family="Syne, sans-serif")),
        xaxis=dict(title="Avg Saturation %", gridcolor="#1e2330", linecolor="#1e2330"),
        yaxis=dict(title="Avg Brightness %", gridcolor="#1e2330", linecolor="#1e2330"),
        height=520,
        legend=dict(font=dict(size=10), itemsizing="constant",
                    title=dict(text="Monument", font=dict(color="#9ca3af"))),
    )
    st.plotly_chart(fig_bub, use_container_width=True)

    # ── Cluster Coverage Treemap ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Color Coverage · Treemap</div>',
                unsafe_allow_html=True)

    agg_tree = (df_lf.groupby(["Monument","Name"])["Pct"]
                .mean().reset_index())
    hex_map_t = df_lf.groupby("Name")["HEX"].first().to_dict()
    agg_tree["HEX"] = agg_tree["Name"].map(hex_map_t)

    fig_tree = px.treemap(
        agg_tree, path=["Monument","Name"],
        values="Pct",
        color="Pct",
        color_continuous_scale=["#0d0f14","#0f4c64","#3db8d8","#80deea"],
        hover_data={"Pct":":.1f"},
    )
    fig_tree.update_traces(
        textfont=dict(family="Syne, sans-serif", size=12),
        marker=dict(line=dict(width=1, color="#0d0f14")),
    )
    fig_tree.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Color Coverage Treemap · Monument → Color Name",
                   font=dict(color="#e8eaf0", size=14, family="Syne, sans-serif")),
        height=480,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(fig_tree, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 · STATISTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab_stat:

    col_sp1, col_sp2 = st.columns(2)
    with col_sp1:
        st.markdown('<div class="section-header">Channel Distributions</div>',
                    unsafe_allow_html=True)

        space_sel = st.selectbox("Color Space", ["RGB","HSV","Lab","LCH"], key="sp_sel")
        df_sp = df_stf[df_stf["Space"] == space_sel].dropna(subset=["Channel","Mean"])

        fig_box = go.Figure()
        channels = df_sp["Channel"].unique()
        for i, ch in enumerate(channels):
            sub = df_sp[df_sp["Channel"] == ch]
            fig_box.add_trace(go.Violin(
                y=sub["Mean"],
                name=ch,
                box_visible=True,
                meanline_visible=True,
                fillcolor=ACCENT[i % len(ACCENT)],
                line_color=ACCENT[i % len(ACCENT)],
                opacity=0.7,
            ))
        fig_box.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text=f"{space_sel} Channel Distributions · Mean per Image",
                       font=dict(color="#e8eaf0", size=14, family="Syne, sans-serif")),
            yaxis=dict(title="Mean Value", gridcolor="#1e2330", linecolor="#1e2330"),
            xaxis=dict(gridcolor="#1e2330", linecolor="#1e2330"),
            showlegend=False,
            height=420,
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with col_sp2:
        st.markdown('<div class="section-header">Mean Values by Monument</div>',
                    unsafe_allow_html=True)

        ch_sel = st.selectbox("Channel", df_stf["Channel"].dropna().unique(),
                              key="ch_sel")
        df_ch = df_stf[df_stf["Channel"] == ch_sel].dropna(subset=["Monument","Mean"])
        agg_ch = (df_ch.groupby("Monument")["Mean"].mean()
                  .sort_values().reset_index())
        agg_ch["short"] = agg_ch["Monument"].str[:28]

        fig_ch = go.Figure(go.Bar(
            y=agg_ch["short"], x=agg_ch["Mean"],
            orientation="h",
            marker=dict(
                color=agg_ch["Mean"],
                colorscale=[[0,"#0e2a3a"],[0.5,"#1a7a9e"],[1,"#80deea"]],
                line=dict(width=0),
            ),
            text=agg_ch["Mean"].round(1),
            textposition="outside",
            textfont=dict(color="#9ca3af", size=10),
        ))
        fig_ch.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text=f"Avg '{ch_sel}' Value per Monument",
                       font=dict(color="#e8eaf0", size=14, family="Syne, sans-serif")),
            xaxis=dict(title=f"Mean {ch_sel}", gridcolor="#1e2330", linecolor="#1e2330"),
            yaxis=dict(autorange="reversed", gridcolor="#1e2330", linecolor="#1e2330",
                       tickfont=dict(size=10)),
            height=420,
        )
        st.plotly_chart(fig_ch, use_container_width=True)

    st.markdown("---")

    # ── Mean RGB radar per monument ───────────────────────────────────────────
    st.markdown('<div class="section-header">RGB Profile Radar · per Monument</div>',
                unsafe_allow_html=True)

    df_rgb_mon = (df_f.groupby("Monument")[["R_mean","G_mean","B_mean",
                                             "S_mean","V_mean","L_mean"]]
                  .mean().reset_index())

    categories = ["R mean","G mean","B mean","S%","V%","L mean"]
    fig_radar = go.Figure()
    for i, row in df_rgb_mon.iterrows():
        vals = [row["R_mean"], row["G_mean"], row["B_mean"],
                row["S_mean"], row["V_mean"], row["L_mean"]]
        vals_norm = [v / max(v, 255) * 100 for v in vals]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals_norm + [vals_norm[0]],
            theta=categories + [categories[0]],
            name=row["Monument"][:28],
            line=dict(color=ACCENT[i % len(ACCENT)], width=1.5),
            fill="toself",
            fillcolor=ACCENT[i % len(ACCENT)].replace("#","rgba(").replace(
                "rgba(","rgba(") + "33" if False else "rgba(0,0,0,0)",
            opacity=0.8,
        ))
    fig_radar.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            bgcolor="#12151c",
            radialaxis=dict(visible=True, range=[0,100],
                            gridcolor="#1e2330", tickcolor="#6b7280",
                            tickfont=dict(size=9)),
            angularaxis=dict(gridcolor="#1e2330", linecolor="#1e2330",
                             tickfont=dict(size=10, color="#9ca3af")),
        ),
        title=dict(text="Normalized Color Channels · Radar per Monument",
                   font=dict(color="#e8eaf0", size=14, family="Syne, sans-serif")),
        legend=dict(font=dict(size=9), itemsizing="constant"),
        height=500,
        margin=dict(l=60, r=60, t=50, b=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    # ── Summary stats table ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">Descriptive Statistics · per Monument</div>',
                unsafe_allow_html=True)

    tbl = (df_f.groupby("Monument")
           .agg(Images=("#","count"),
                R_avg=("R_mean","mean"), G_avg=("G_mean","mean"),
                B_avg=("B_mean","mean"), S_avg=("S_mean","mean"),
                V_avg=("V_mean","mean"), L_avg=("L_mean","mean"))
           .round(1).reset_index())
    tbl.columns = ["Monument","Images","R avg","G avg","B avg","S% avg","V% avg","L avg"]

    st.dataframe(
        tbl,
        use_container_width=True,
        height=min(400, 40 + len(tbl) * 38),
        column_config={
            "Monument": st.column_config.TextColumn("Monument"),
            "Images": st.column_config.NumberColumn("📷 Images", format="%d"),
            "R avg": st.column_config.ProgressColumn("R avg", min_value=0, max_value=255, format="%.0f"),
            "G avg": st.column_config.ProgressColumn("G avg", min_value=0, max_value=255, format="%.0f"),
            "B avg": st.column_config.ProgressColumn("B avg", min_value=0, max_value=255, format="%.0f"),
            "S% avg": st.column_config.ProgressColumn("Saturation %", min_value=0, max_value=100, format="%.1f"),
            "V% avg": st.column_config.ProgressColumn("Brightness %", min_value=0, max_value=100, format="%.1f"),
        },
        hide_index=True,
    )
