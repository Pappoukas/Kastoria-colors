import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import colorsys

st.set_page_config(
    page_title="Kastoria · Color Intelligence",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0d0f14; color: #e8eaf0; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1400px; }
[data-testid="stSidebar"] { background: #12151c !important; border-right: 1px solid #1e2330; }
[data-testid="stSidebarContent"] { padding: 2rem 1.2rem; }
.app-title {
    font-family: 'Syne', sans-serif; font-size: 2.5rem; font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, #64b5f6, #4dd0e1, #80cbc4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin: 0 0 0.2rem; line-height: 1.1;
}
.app-subtitle { font-size: 0.85rem; color: #4b5563; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 1.8rem; }
.metric-grid { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
.metric-card {
    background: #12151c; border: 1px solid #1e2330; border-radius: 12px;
    padding: 1.1rem 1.4rem; flex: 1; min-width: 150px; position: relative; overflow: hidden;
}
.metric-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #64b5f6, #4dd0e1);
}
.metric-value { font-family: 'Syne', sans-serif; font-size: 1.9rem; font-weight: 700; color: #e8eaf0; line-height: 1; }
.metric-label { font-size: 0.72rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.3rem; }
.section-header {
    font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700;
    color: #4dd0e1; text-transform: uppercase; letter-spacing: 0.12em;
    margin: 1.8rem 0 0.8rem; border-bottom: 1px solid #1e2330; padding-bottom: 0.5rem;
}
.stTabs [data-baseweb="tab-list"] { background: #12151c; border-radius: 10px; padding: 4px; gap: 2px; border: 1px solid #1e2330; }
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 7px; color: #6b7280;
    font-family: 'Syne', sans-serif; font-weight: 600; font-size: 0.85rem;
    letter-spacing: 0.05em; padding: 0.5rem 1.3rem;
}
.stTabs [aria-selected="true"] { background: linear-gradient(135deg,#1a2744,#162535) !important; color: #4dd0e1 !important; border: 1px solid #1e3a5f !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem; }
.stSelectbox label, .stRadio label, .stSlider label { color: #9ca3af !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: 0.06em; }
hr { border-color: #1e2330; margin: 1.5rem 0; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d0f14; }
::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme helpers ───────────────────────────────────────────────────────
# xaxis/yaxis are deliberately NOT in PL_BASE to avoid "duplicate keyword argument"
# TypeError when callers also pass xaxis/yaxis to update_layout.
PL_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(18,21,28,0.95)",
    font=dict(family="Inter, sans-serif", color="#9ca3af", size=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
    coloraxis_colorbar=dict(tickfont=dict(color="#9ca3af")),
)
_DEF_MARGIN = dict(l=14, r=14, t=48, b=14)
_TITLE_FONT = dict(family="Syne, sans-serif", color="#e8eaf0", size=14)
AX = dict(gridcolor="#1e2330", zerolinecolor="#1e2330", linecolor="#1e2330",
          tickfont=dict(color="#9ca3af"))

def theme(fig, title="", height=420, xkw=None, ykw=None, margin=None, extra=None):
    """Apply dark theme. Builds a single merged dict — zero duplicate-kwarg risk."""
    layout = dict(PL_BASE)                          # shallow copy of base
    layout["title"]  = dict(text=title, font=_TITLE_FONT)
    layout["height"] = height
    layout["margin"] = margin if margin is not None else _DEF_MARGIN
    if extra:
        layout.update(extra)                        # extra always wins
    fig.update_layout(**layout)
    fig.update_xaxes(**{**AX, **(xkw or {})})
    fig.update_yaxes(**{**AX, **(ykw or {})})
    return fig

ACCENT = ["#64b5f6","#4dd0e1","#80cbc4","#a5d6a7","#fff176",
          "#ffb74d","#ef9a9a","#ce93d8","#f48fb1","#80deea"]


# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    path = "color_summary_batch.xlsx"
    df = pd.read_excel(path, sheet_name="Summary", header=2)
    df.columns = [
        "#","URL","Filename","ID","Monument","WxH",
        "R_mean","G_mean","B_mean","H_mean","S_mean","V_mean","L_mean","C_mean",
        "C1_hex","C1_pct","C1_name","C2_hex","C2_pct","C2_name",
        "C3_hex","C3_pct","C3_name","C4_hex","C4_pct","C4_name",
        "C5_hex","C5_pct","C5_name","Status",
    ]
    df = df.dropna(subset=["Monument"])
    for c in ["R_mean","G_mean","B_mean","H_mean","S_mean","V_mean","L_mean","C_mean",
              "C1_pct","C2_pct","C3_pct","C4_pct","C5_pct","#"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["#"])
    mon_map = df[["#","Monument"]].drop_duplicates("#")

    raw = pd.read_excel(path, sheet_name="Clusters", header=0)
    raw.columns = raw.iloc[0]
    cl = raw.iloc[1:].reset_index(drop=True)
    cl.columns = ["#","URL","Filename","Cluster","Pixels","Pct","HEX",
                  "Swatch","R","G","B","H","S","V","L","a","b","Name"]
    for c in ["#","Pixels","Pct","R","G","B","H","S","V","L","a","b"]:
        cl[c] = pd.to_numeric(cl[c], errors="coerce")
    cl = cl.dropna(subset=["#"]).merge(mon_map, on="#", how="left")

    st_df = pd.read_excel(path, sheet_name="Statistics", header=2)
    st_df.columns = ["#","URL","Filename","Space","Channel",
                     "Mean","Median","Min","Max","Std","_1","_2","_3"]
    for c in ["#","Mean","Median","Min","Max","Std"]:
        st_df[c] = pd.to_numeric(st_df[c], errors="coerce")
    st_df = st_df.dropna(subset=["Space","Channel"]).merge(mon_map, on="#", how="left")

    return df, cl, st_df, mon_map


@st.cache_data
def melt_colors(df):
    frames = []
    for i in range(1, 6):
        tmp = df[["#","Monument",f"C{i}_hex",f"C{i}_pct",f"C{i}_name"]].copy()
        tmp.columns = ["#","Monument","HEX","Pct","Name"]
        tmp["Rank"] = i
        frames.append(tmp)
    out = pd.concat(frames, ignore_index=True).dropna(subset=["Name","Pct"])
    out["Name"] = out["Name"].str.strip()
    return out


with st.spinner("Loading color data…"):
    df_sum, df_cl, df_stat, mon_map = load_data()
    df_long = melt_colors(df_sum)

monuments = sorted(df_sum["Monument"].dropna().unique())

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<p class="app-title">Kastoria · Color Intelligence</p>
<p class="app-subtitle">TripAdvisor Visitor Photo Analysis · Color Profiling System</p>
""", unsafe_allow_html=True)

n_img = int(df_sum["#"].nunique())
n_pl  = int(df_sum["Monument"].nunique())
n_cl  = int(df_cl.shape[0])
n_co  = int(df_long["Name"].nunique())

st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card"><div class="metric-value">{n_img:,}</div><div class="metric-label">Images Analyzed</div></div>
  <div class="metric-card"><div class="metric-value">{n_pl}</div><div class="metric-label">Monuments / POIs</div></div>
  <div class="metric-card"><div class="metric-value">{n_cl:,}</div><div class="metric-label">Color Clusters</div></div>
  <div class="metric-card"><div class="metric-value">{n_co}</div><div class="metric-label">Unique Color Names</div></div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎛 Filters")
    st.markdown("---")
    sel_mon = st.multiselect("Monuments / POIs", options=monuments, default=monuments)
    if not sel_mon:
        sel_mon = monuments
    st.markdown("---")
    st.markdown("### 🗃 Data File")
    st.code("color_summary_batch.xlsx", language=None)
    st.caption("Place in repo root → deploy via Streamlit Cloud.")
    st.markdown("---")
    st.markdown("""<div style="font-size:0.72rem;color:#4b5563;line-height:1.8">
    Built with <strong style="color:#4dd0e1">Streamlit</strong> · Plotly<br>
    Data: TripAdvisor · Kastoria, Greece<br>Color extraction: Image Color Summarizer
    </div>""", unsafe_allow_html=True)

# ── Filtered ──────────────────────────────────────────────────────────────────
df_f  = df_sum[df_sum["Monument"].isin(sel_mon)]
df_lf = df_long[df_long["Monument"].isin(sel_mon)]
df_cf = df_cl[df_cl["Monument"].isin(sel_mon)]
df_sf = df_stat[df_stat["Monument"].isin(sel_mon)]

def shorten(m):
    return (m.replace("Cave of Dragon (Spilia tou drakou)", "Dragon Cave")
             .replace("Church of St. Taksiarkhov u Mitropolii", "St. Taksiarhov")
             .replace("Church of the Panagia Koumbelidiki", "Koumbelidiki")
             .replace("Culture 8 Cultural City and Nature Guided Day Tours", "Culture 8")
             .replace("Kastorian Byzantine Churches.", "Byzantine Ch.")
             .replace("Panagia Mavriotissa Monastery", "Mavriotissa")
             .replace("Wax Museum  of Mavrochoriou Kastorias", "Wax Museum")
             .replace("Byzantine Museum of Kastoria", "Byzantine Museum"))


# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["🎨  Summary", "🔵  Clusters", "📊  Statistics"])


# ── TAB 1: SUMMARY ────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="section-header">Color Frequency</div>', unsafe_allow_html=True)

    mode = st.radio("View mode",
                    ["🌐  Top 10 Colors — Overall", "📍  Top 5 Colors — per Monument"],
                    horizontal=True)
    hex_map = df_lf.groupby("Name")["HEX"].first().to_dict()

    if "Overall" in mode:
        agg = (df_lf.groupby("Name")["Pct"].mean()
               .sort_values(ascending=False).head(10).reset_index())
        bar_title = "Top 10 Dominant Colors · Avg Coverage %"
        bar_h = 420
    else:
        mon_pick = st.selectbox("Select Monument", sel_mon, key="bar_mon")
        agg = (df_lf[df_lf["Monument"] == mon_pick]
               .groupby("Name")["Pct"].mean()
               .sort_values(ascending=False).head(5).reset_index())
        bar_title = f"Top 5 Colors · {mon_pick}"
        bar_h = 320

    agg["color"] = agg["Name"].map(hex_map).fillna("#4dd0e1")
    fig_bar = go.Figure(go.Bar(
        x=agg["Pct"], y=agg["Name"], orientation="h",
        marker=dict(color=agg["color"].tolist(), line=dict(width=0)),
        text=agg["Pct"].round(1).astype(str) + "%",
        textposition="outside",
        textfont=dict(color="#9ca3af", size=11),
    ))
    theme(fig_bar, title=bar_title, height=bar_h,
          xkw=dict(title="Avg % Coverage"),
          ykw=dict(autorange="reversed", tickfont=dict(color="#c9d1d9")))
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    col_a, col_b = st.columns([1, 1.6], gap="large")

    with col_a:
        st.markdown('<div class="section-header">Dominant Colors Pie</div>', unsafe_allow_html=True)
        dom = (df_lf[df_lf["Rank"] == 1].groupby("Name")["Pct"].mean()
               .sort_values(ascending=False).head(12).reset_index())
        dom["color"] = dom["Name"].map(hex_map).fillna("#4dd0e1")
        fig_pie = go.Figure(go.Pie(
            labels=dom["Name"], values=dom["Pct"], hole=0.52,
            marker=dict(colors=dom["color"].tolist(),
                        line=dict(color="#0d0f14", width=2)),
            textinfo="label+percent",
            textfont=dict(size=10, color="#e8eaf0"),
            hovertemplate="<b>%{label}</b><br>Avg: %{value:.1f}%<extra></extra>",
        ))
        fig_pie.add_annotation(text=f"<b>{n_img}</b><br>images",
                               x=0.5, y=0.5, showarrow=False,
                               font=dict(size=13, color="#e8eaf0", family="Syne, sans-serif"))
        theme(fig_pie, title="Dominant Color Share", height=400,
              margin=dict(l=10, r=10, t=48, b=10), extra=dict(showlegend=False))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Color Intensity Heatmap</div>', unsafe_allow_html=True)
        top12 = (df_lf.groupby("Name")["Pct"].mean()
                 .sort_values(ascending=False).head(12).index.tolist())
        pivot = (df_lf[df_lf["Name"].isin(top12)]
                 .groupby(["Monument","Name"])["Pct"].mean()
                 .unstack(fill_value=0)
                 .reindex(columns=[c for c in top12 if c in df_lf["Name"].unique()]))
        pivot.index = [shorten(m) for m in pivot.index]
        short_sel = [shorten(m) for m in sel_mon]
        pivot = pivot.loc[[r for r in short_sel if r in pivot.index]]

        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
            colorscale=[[0,"#0d0f14"],[0.25,"#0e2a3a"],[0.5,"#0f4c64"],
                        [0.75,"#1a7a9e"],[1,"#80deea"]],
            hoverongaps=False,
            hovertemplate="<b>%{y}</b> × <b>%{x}</b><br>Avg: %{z:.1f}%<extra></extra>",
            xgap=2, ygap=2,
        ))
        theme(fig_heat, title="Monuments × Color Name · Avg Coverage %", height=400,
              xkw=dict(tickangle=-35, tickfont=dict(size=10), side="bottom", showgrid=False),
              ykw=dict(tickfont=dict(size=10), autorange="reversed", showgrid=False))
        fig_heat.update_layout(margin=dict(l=10, r=20, t=48, b=95))
        st.plotly_chart(fig_heat, use_container_width=True)


# ── TAB 2: CLUSTERS ───────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-header">Brightness vs Saturation — Scatter</div>',
                unsafe_allow_html=True)

    df_sc = df_cf.dropna(subset=["S","V","HEX","Monument"])
    c1, c2 = st.columns([3, 1])
    with c2:
        n_pts  = st.slider("Max points", 500, min(8000, len(df_sc)),
                           min(3000, len(df_sc)), 500)
        col_by = st.selectbox("Color by", ["Monument","Color Name","Actual HEX"])

    df_samp = df_sc.sample(n=min(n_pts, len(df_sc)), random_state=42)

    if col_by == "Actual HEX":
        fig_sc = go.Figure(go.Scatter(
            x=df_samp["S"], y=df_samp["V"], mode="markers",
            marker=dict(color=df_samp["HEX"].tolist(), size=5, opacity=0.75,
                        line=dict(width=0)),
            text=df_samp["Name"],
            hovertemplate="<b>%{text}</b><br>S: %{x:.1f}%  V: %{y:.1f}%<extra></extra>",
        ))
    else:
        field = "Monument" if col_by == "Monument" else "Name"
        fig_sc = px.scatter(df_samp, x="S", y="V", color=field,
                            color_discrete_sequence=ACCENT, opacity=0.72,
                            hover_data={"HEX":True,"Name":True,"Pct":True})
        fig_sc.update_traces(marker=dict(size=5))

    theme(fig_sc, title="Color Clusters · Saturation vs Brightness", height=460,
          xkw=dict(title="Saturation %", range=[-2,102]),
          ykw=dict(title="Brightness %", range=[-2,102]))
    fig_sc.update_layout(legend=dict(font=dict(size=9), itemsizing="constant"))
    with c1:
        st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Color Profile Clusters · Bubble Chart</div>',
                unsafe_allow_html=True)
    st.caption("Each bubble = aggregated color cluster per monument. Size = avg pixel coverage %.")

    def hsv_hex(h, s, v):
        r, g, b = colorsys.hsv_to_rgb(h/360, s/100, v/100)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    agg_cl = (df_cf.groupby(["Monument","Name"])
              .agg(Pct=("Pct","mean"), V=("V","mean"), S=("S","mean"), H=("H","mean"))
              .reset_index().dropna())
    agg_cl = agg_cl[agg_cl["Pct"] > 1.5]
    agg_cl["color"] = agg_cl.apply(lambda r: hsv_hex(r["H"],r["S"],r["V"]), axis=1)

    fig_bub = px.scatter(agg_cl, x="S", y="V", size="Pct", color="Monument",
                         color_discrete_sequence=ACCENT, text="Name", size_max=50,
                         hover_data={"Monument":True,"Name":True,"Pct":":.1f","S":":.0f","V":":.0f"})
    fig_bub.update_traces(textfont=dict(size=9, color="rgba(255,255,255,0.5)"),
                          textposition="top center")
    theme(fig_bub, title="Aggregated Color Clusters · Bubble = Avg Coverage", height=520,
          xkw=dict(title="Avg Saturation %"),
          ykw=dict(title="Avg Brightness %"))
    fig_bub.update_layout(legend=dict(font=dict(size=9), itemsizing="constant"))
    st.plotly_chart(fig_bub, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Color Coverage Treemap</div>', unsafe_allow_html=True)

    agg_tree = df_lf.groupby(["Monument","Name"])["Pct"].mean().reset_index()
    fig_tree = px.treemap(agg_tree, path=["Monument","Name"], values="Pct",
                          color="Pct",
                          color_continuous_scale=["#0d0f14","#0f4c64","#3db8d8","#80deea"])
    fig_tree.update_traces(textfont=dict(family="Syne, sans-serif", size=11),
                           marker=dict(line=dict(width=1, color="#0d0f14")))
    theme(fig_tree, title="Color Coverage · Monument → Color Name",
          height=480, margin=dict(l=10,r=10,t=48,b=10))
    st.plotly_chart(fig_tree, use_container_width=True)


# ── TAB 3: STATISTICS ─────────────────────────────────────────────────────────
with tab3:
    cx, cy = st.columns(2, gap="large")

    with cx:
        st.markdown('<div class="section-header">Channel Distributions</div>',
                    unsafe_allow_html=True)
        space = st.selectbox("Color Space", ["RGB","HSV","Lab","LCH"])
        df_sp = df_sf[df_sf["Space"] == space].dropna(subset=["Channel","Mean"])
        fig_vio = go.Figure()
        for i, ch in enumerate(df_sp["Channel"].unique()):
            sub = df_sp[df_sp["Channel"] == ch]
            fig_vio.add_trace(go.Violin(
                y=sub["Mean"], name=ch, box_visible=True, meanline_visible=True,
                fillcolor=ACCENT[i % len(ACCENT)],
                line_color=ACCENT[i % len(ACCENT)], opacity=0.65,
            ))
        theme(fig_vio, title=f"{space} · Channel Mean Distributions", height=420,
              ykw=dict(title="Mean Value"))
        fig_vio.update_layout(showlegend=False)
        st.plotly_chart(fig_vio, use_container_width=True)

    with cy:
        st.markdown('<div class="section-header">Mean Values by Monument</div>',
                    unsafe_allow_html=True)
        ch = st.selectbox("Channel", df_sf["Channel"].dropna().unique())
        df_ch = (df_sf[df_sf["Channel"] == ch].dropna(subset=["Monument","Mean"])
                 .groupby("Monument")["Mean"].mean().sort_values().reset_index())
        df_ch["label"] = df_ch["Monument"].apply(shorten)
        fig_ch = go.Figure(go.Bar(
            y=df_ch["label"], x=df_ch["Mean"], orientation="h",
            marker=dict(color=df_ch["Mean"],
                        colorscale=[[0,"#0e2a3a"],[0.5,"#1a7a9e"],[1,"#80deea"]],
                        line=dict(width=0)),
            text=df_ch["Mean"].round(1), textposition="outside",
            textfont=dict(color="#9ca3af", size=10),
        ))
        theme(fig_ch, title=f"Avg '{ch}' per Monument", height=420,
              xkw=dict(title=f"Mean {ch}"),
              ykw=dict(autorange="reversed", tickfont=dict(size=10)))
        st.plotly_chart(fig_ch, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">RGB/HSV Radar · per Monument</div>',
                unsafe_allow_html=True)

    df_rad = df_f.groupby("Monument")[["R_mean","G_mean","B_mean",
                                        "S_mean","V_mean","L_mean"]].mean().reset_index()
    cats = ["R","G","B","S%","V%","L"]
    fig_rad = go.Figure()
    for i, row in df_rad.iterrows():
        vals = [row["R_mean"]/255*100, row["G_mean"]/255*100, row["B_mean"]/255*100,
                row["S_mean"], row["V_mean"], row["L_mean"]]
        fig_rad.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=cats + [cats[0]],
            name=shorten(row["Monument"])[:26],
            line=dict(color=ACCENT[i % len(ACCENT)], width=1.5),
            fill="toself", fillcolor="rgba(0,0,0,0)", opacity=0.85,
        ))
    theme(fig_rad, title="Normalized Color Channels · Radar per Monument",
          height=500, margin=dict(l=70,r=70,t=54,b=24),
          extra=dict(
              polar=dict(
                  bgcolor="#12151c",
                  radialaxis=dict(visible=True, range=[0,100], gridcolor="#1e2330",
                                  tickcolor="#6b7280", tickfont=dict(size=9)),
                  angularaxis=dict(gridcolor="#1e2330", linecolor="#1e2330",
                                   tickfont=dict(size=10, color="#9ca3af")),
              ),
              legend=dict(font=dict(size=9), itemsizing="constant"),
          ))
    st.plotly_chart(fig_rad, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Descriptive Statistics · per Monument</div>',
                unsafe_allow_html=True)

    tbl = (df_f.groupby("Monument")
           .agg(Images=("#","count"),
                R=("R_mean","mean"), G=("G_mean","mean"), B=("B_mean","mean"),
                S=("S_mean","mean"), V=("V_mean","mean"), L=("L_mean","mean"))
           .round(1).reset_index())
    tbl.columns = ["Monument","Images","R avg","G avg","B avg","S% avg","V% avg","L avg"]
    st.dataframe(
        tbl, use_container_width=True,
        height=min(420, 44 + len(tbl)*38),
        column_config={
            "Monument": st.column_config.TextColumn("Monument"),
            "Images": st.column_config.NumberColumn("📷", format="%d"),
            "R avg": st.column_config.ProgressColumn("R", min_value=0, max_value=255, format="%.0f"),
            "G avg": st.column_config.ProgressColumn("G", min_value=0, max_value=255, format="%.0f"),
            "B avg": st.column_config.ProgressColumn("B", min_value=0, max_value=255, format="%.0f"),
            "S% avg": st.column_config.ProgressColumn("Saturation %", min_value=0, max_value=100, format="%.1f"),
            "V% avg": st.column_config.ProgressColumn("Brightness %", min_value=0, max_value=100, format="%.1f"),
        },
        hide_index=True,
    )
