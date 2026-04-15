"""Page 11: OAS Retirement Planner — Couple's Old Age Security calculator with shortfall analysis."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

from dashboard.components.styles import apply_custom_css

st.set_page_config(page_title="OAS Planner", page_icon="🇨🇦", layout="wide")
apply_custom_css()
st.title("OAS Retirement Planner")
st.caption(
    "Old Age Security income calculator for Canadian couples — "
    "accounts for different ages and independent OAS start dates"
)

# ─── Constants ───────────────────────────────────────────────────────────────
CURRENT_YEAR = datetime.now().year
OAS_BASE_MONTHLY = 727.67   # Approximate 2025 Q4 rate for ages 65–74
OAS_75_TOPUP = 0.10         # Government adds 10% automatically at age 75
OAS_DEFER_RATE = 0.006      # 0.6% per month deferred past 65


def oas_factor(start_age: int) -> float:
    """Multiplier applied to OAS_BASE_MONTHLY for a given start age (65–70)."""
    return 1.0 + (start_age - 65) * 12 * OAS_DEFER_RATE


# ─── Section 1: Profiles ─────────────────────────────────────────────────────
st.subheader("Your Profiles")

left, right = st.columns(2)

with left:
    st.markdown("**Person 1 (You)**")
    age1 = st.number_input("Current Age", min_value=18, max_value=64, value=45, step=1, key="age1")
    oas_start1 = st.slider(
        "OAS Start Age", min_value=65, max_value=70, value=65, key="oas1",
        help="0.6% per month bonus for each month deferred past 65 (7.2%/yr, max 36% at 70).",
    )
    cpp1 = st.number_input(
        "Estimated CPP (monthly, CAD)", min_value=0, max_value=1500, value=300, step=50, key="cpp1",
        help="From My Service Canada Account.",
    )
    birth_year1 = CURRENT_YEAR - age1
    oas_start_year1 = birth_year1 + oas_start1
    years_to_oas1 = oas_start_year1 - CURRENT_YEAR
    st.metric("OAS Starts", f"Year {oas_start_year1}", f"In {years_to_oas1} years")

with right:
    st.markdown("**Person 2 (Spouse)**")
    age2 = st.number_input("Current Age", min_value=18, max_value=64, value=43, step=1, key="age2")
    oas_start2 = st.slider(
        "OAS Start Age", min_value=65, max_value=70, value=65, key="oas2",
        help="0.6% per month bonus for each month deferred past 65 (7.2%/yr, max 36% at 70).",
    )
    cpp2 = st.number_input(
        "Estimated CPP (monthly, CAD)", min_value=0, max_value=1500, value=300, step=50, key="cpp2",
        help="From My Service Canada Account.",
    )
    birth_year2 = CURRENT_YEAR - age2
    oas_start_year2 = birth_year2 + oas_start2
    years_to_oas2 = oas_start_year2 - CURRENT_YEAR
    st.metric("OAS Starts", f"Year {oas_start_year2}", f"In {years_to_oas2} years")

# Derived OAS benefit amounts (today's dollars)
base_monthly1 = OAS_BASE_MONTHLY * oas_factor(oas_start1)
base_monthly2 = OAS_BASE_MONTHLY * oas_factor(oas_start2)
monthly_at_75_1 = base_monthly1 * (1 + OAS_75_TOPUP)
monthly_at_75_2 = base_monthly2 * (1 + OAS_75_TOPUP)

earlier_start_year = min(oas_start_year1, oas_start_year2)
later_start_year = max(oas_start_year1, oas_start_year2)

# ─── Section 2: OAS Benefit Summary ──────────────────────────────────────────
st.subheader("OAS Benefit Summary")

col_l, col_r = st.columns(2)

for col, label, base_mo, at_75, start_age, start_year in [
    (col_l, "Person 1 (You)", base_monthly1, monthly_at_75_1, oas_start1, oas_start_year1),
    (col_r, "Person 2 (Spouse)", base_monthly2, monthly_at_75_2, oas_start2, oas_start_year2),
]:
    with col:
        st.markdown(f"**{label}** — starts age {start_age} ({start_year})")
        ma, mb = st.columns(2)
        ma.metric("Monthly at Start", f"${base_mo:,.2f}")
        mb.metric("Monthly after 75", f"${at_75:,.2f}", f"+${at_75 - base_mo:,.2f}")

        ages_range = list(range(65, 71))
        vals = [OAS_BASE_MONTHLY * oas_factor(a) for a in ages_range]
        bar_colors = ["#ff9800" if a == start_age else "#1e88e5" for a in ages_range]
        fig_mini = go.Figure(go.Bar(
            x=[str(a) for a in ages_range],
            y=vals,
            marker_color=bar_colors,
            text=[f"${v:,.0f}" for v in vals],
            textposition="outside",
        ))
        fig_mini.update_layout(
            template="plotly_white",
            title=f"{label}",
            xaxis_title="Start Age",
            yaxis=dict(tickprefix="$", tickformat=",.0f", range=[0, max(vals) * 1.18]),
            height=270,
            margin=dict(l=20, r=10, t=40, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_mini, use_container_width=True)

st.info(
    "**Age 75 top-up:** The Government of Canada automatically increases OAS by **10%** "
    "when each person turns 75, regardless of when they started collecting."
)

# Combined income summary
combined_both = base_monthly1 + base_monthly2 + cpp1 + cpp2
c1, c2, c3 = st.columns(3)
c1.metric("Person 1 OAS + CPP", f"${base_monthly1 + cpp1:,.0f}/mo", f"from {oas_start_year1}")
c2.metric("Person 2 OAS + CPP", f"${base_monthly2 + cpp2:,.0f}/mo", f"from {oas_start_year2}")
c3.metric("Combined (both collecting)", f"${combined_both:,.0f}/mo", f"from {later_start_year}")

# ─── Section 3: Household Spending & Settings ─────────────────────────────────
st.subheader("Household Spending & Settings")

younger_age = min(age1, age2)
sp1, sp2, sp3 = st.columns(3)
with sp1:
    spending_monthly = st.number_input(
        "Desired Monthly Household Spending (CAD)",
        min_value=500, max_value=30000, value=5000, step=100,
    )
with sp2:
    retirement_year = st.number_input(
        "Retirement Start Year",
        min_value=CURRENT_YEAR, max_value=2100,
        value=min(oas_start_year1, oas_start_year2), step=1,
        help=(
            "The year you stop working and the portfolio starts being drawn on. "
            "Can be before OAS starts — the full spending is funded by the portfolio "
            "until each person's OAS kicks in."
        ),
    )
with sp3:
    plan_to_age = st.number_input(
        "Plan To Age (younger person)",
        min_value=66, max_value=100, value=90, step=1,
        help=f"Projection runs until the younger person (currently {younger_age}) reaches this age.",
    )

# ─── Inflation ────────────────────────────────────────────────────────────────
inf1, inf2 = st.columns([1, 3])
with inf1:
    use_inflation = st.toggle(
        "Adjust for Inflation", value=False,
        help="OAS is CPI-indexed quarterly by law. Toggle on to show nominal dollar projections.",
    )
with inf2:
    if use_inflation:
        inflation_rate = st.slider(
            "Annual Inflation Rate (%)", min_value=1.0, max_value=5.0, value=2.5, step=0.1,
        ) / 100
        st.caption(
            "OAS, CPP, and spending all grow at this rate. "
            "Since OAS is CPI-indexed, the shortfall is primarily driven by when each person starts collecting."
        )
    else:
        inflation_rate = 0.0
        st.caption("All figures in today's dollars.")

# ─── Portfolio Return ─────────────────────────────────────────────────────────
return_label = (
    "Expected Nominal Portfolio Return (% / yr)"
    if use_inflation
    else "Expected Real Portfolio Return (% / yr, after inflation)"
)
portfolio_return = st.slider(
    return_label,
    min_value=1.0, max_value=12.0, value=5.0, step=0.25,
    help=(
        "Average annual return you expect from your investment portfolio. "
        + (
            "Inflation is ON — enter a nominal rate (e.g. 7.5% = 5% real + 2.5% inflation)."
            if use_inflation
            else "Inflation is OFF — enter a real rate above inflation (e.g. 5% real ≈ 7.5% nominal − 2.5% inflation)."
        )
    ),
) / 100

# ─── Section 4: Shortfall Analysis ───────────────────────────────────────────
st.subheader("Shortfall Analysis")

proj_start_year = retirement_year
proj_end_year = CURRENT_YEAR + (plan_to_age - younger_age)
pre_oas_years = max(0, earlier_start_year - retirement_year)

if proj_end_year <= proj_start_year:
    st.warning("Increase 'Plan To Age' — the projection end must be after the retirement start year.")
    st.stop()

# ── Year-by-year projection ──
proj_rows = []
cumulative_shortfall = 0.0

for cal_year in range(proj_start_year, proj_end_year + 1):
    years_from_now = cal_year - CURRENT_YEAR
    inf_factor = (1 + inflation_rate) ** years_from_now

    age1_yr = cal_year - birth_year1
    age2_yr = cal_year - birth_year2

    # OAS for each person: 0 until their start year, then base × top-up if ≥75 × inflation
    oas1_yr = 0.0
    if cal_year >= oas_start_year1:
        topup1 = (1 + OAS_75_TOPUP) if age1_yr >= 75 else 1.0
        oas1_yr = base_monthly1 * topup1 * inf_factor

    oas2_yr = 0.0
    if cal_year >= oas_start_year2:
        topup2 = (1 + OAS_75_TOPUP) if age2_yr >= 75 else 1.0
        oas2_yr = base_monthly2 * topup2 * inf_factor

    # CPP starts when each person's OAS starts
    cpp1_yr = cpp1 * inf_factor if cal_year >= oas_start_year1 else 0.0
    cpp2_yr = cpp2 * inf_factor if cal_year >= oas_start_year2 else 0.0

    spending_yr = spending_monthly * inf_factor
    total_income_yr = oas1_yr + oas2_yr + cpp1_yr + cpp2_yr
    shortfall_yr = (spending_yr - total_income_yr) * 12  # annualised
    cumulative_shortfall += shortfall_yr

    proj_rows.append({
        "Year": cal_year,
        "P1 Age": age1_yr,
        "P2 Age": age2_yr,
        "P1 OAS (mo)": oas1_yr,
        "P2 OAS (mo)": oas2_yr,
        "CPP Combined (mo)": cpp1_yr + cpp2_yr,
        "Total Income (mo)": total_income_yr,
        "Spending (mo)": spending_yr,
        "Annual Shortfall": shortfall_yr,
        "Cumulative Shortfall": cumulative_shortfall,
    })

df_proj = pd.DataFrame(proj_rows)

# Shortfall at first OAS year
shortfall_first = df_proj.iloc[0]["Annual Shortfall"] / 12

# Shortfall once both are collecting
both_rows = df_proj[df_proj["Year"] >= later_start_year]
shortfall_both = both_rows.iloc[0]["Annual Shortfall"] / 12 if not both_rows.empty else shortfall_first

# Nest egg: PV of the full shortfall stream at the portfolio return rate.
# Surpluses (negative shortfalls) are included — the portfolio earns during those years,
# reducing how much you need upfront. Formula: sum(S_i / (1+r)^(i+1))
shortfall_series = df_proj["Annual Shortfall"].tolist()
nest_egg = max(0.0, sum(s / (1 + portfolio_return) ** (i + 1) for i, s in enumerate(shortfall_series)))

# Year-by-year portfolio balance simulation
# balance grows at portfolio_return each year, then covers the annual shortfall
balance = nest_egg
port_balances = []
for s in shortfall_series:
    balance = balance * (1 + portfolio_return) - s
    port_balances.append(balance)
df_proj["Portfolio Balance"] = port_balances

# Nest egg today: PV of the full nest egg discounted back to today at portfolio return
years_to_retirement = retirement_year - CURRENT_YEAR
months_to_save = years_to_retirement * 12
nest_egg_today = nest_egg / (1 + portfolio_return) ** years_to_retirement if years_to_retirement > 0 else nest_egg

total_shortfall = max(0.0, df_proj["Annual Shortfall"].sum())

# Pre-OAS callout
if pre_oas_years > 0:
    st.info(
        f"You're retiring **{pre_oas_years} year{'s' if pre_oas_years != 1 else ''} before first OAS** ({earlier_start_year}). "
        f"The portfolio funds **100% of spending** (${spending_monthly:,.0f}/mo today) during that gap — "
        f"this is the most portfolio-intensive phase and is the primary driver of your nest egg size."
    )

# ── Summary metrics ──
s1, s2, s3, s4 = st.columns(4)
s1_label = f"Monthly Draw at Retirement ({retirement_year})" if pre_oas_years > 0 else f"Shortfall at Retirement ({retirement_year})"
s1_help = (
    f"Full spending funded by portfolio in {retirement_year} — no OAS yet, first starts in {earlier_start_year}."
    if pre_oas_years > 0
    else f"Monthly shortfall at retirement — OAS already in payment."
)
s1.metric(s1_label, f"${max(0, shortfall_first):,.0f}/mo", help=s1_help)
s2.metric(
    f"Shortfall from {later_start_year}",
    f"${max(0, shortfall_both):,.0f}/mo",
    help="Once both are collecting OAS + CPP.",
)
lbl = "Nominal" if use_inflation else "Today's"
s3.metric(
    f"Total Lifetime Shortfall ({lbl} $)",
    f"${total_shortfall:,.0f}",
    help=f"Sum of all annual shortfalls from {proj_start_year} to {proj_end_year}.",
)
s4.metric(
    "Nest Egg Needed",
    f"${nest_egg:,.0f}",
    help=(
        f"Lump sum needed at retirement (year {proj_start_year}) assuming your portfolio earns "
        f"{portfolio_return*100:.2g}%/yr. Sized so the portfolio reaches $0 at age {plan_to_age} of the younger person. "
        "Accounts for the shortfall decreasing when the second person's OAS kicks in."
    ),
)

# ── Portfolio Today ───────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Portfolio Today")
dollar_mode = "nominal" if use_inflation else "today's"
st.caption(
    f"Everything below is in **{dollar_mode} dollars** — same units as the nest egg figures above. "
    f"Enter your current portfolio and see exactly where you stand today."
)

current_portfolio = st.number_input(
    "Your Current Portfolio Value (CAD)",
    min_value=0, max_value=10_000_000, value=0, step=5000,
    help="Enter what you have invested today across all accounts (RRSP, TFSA, non-registered, etc.).",
)

# ── Today's dollar comparison ──
gap_today = nest_egg_today - current_portfolio  # positive = gap, negative = surplus

# ── Future (retirement-year) dollar comparison ──
projected_at_retirement = current_portfolio * (1 + portfolio_return) ** years_to_retirement
future_gap = nest_egg - projected_at_retirement  # positive = gap, negative = surplus

# Monthly savings to close the gap (PMT on the retirement-dollar gap)
if future_gap > 0 and months_to_save > 0:
    r_mo = (1 + portfolio_return) ** (1 / 12) - 1
    monthly_savings_to_close = future_gap * r_mo / ((1 + r_mo) ** months_to_save - 1)
else:
    monthly_savings_to_close = 0.0

# ── Row 1: Today ──
st.caption(f"**Today ({CURRENT_YEAR})**")
p1, p2, p3 = st.columns(3)
p1.metric(
    "Nest Egg Needed Today",
    f"${nest_egg_today:,.0f}",
    help=(
        f"Invest this lump sum today, add nothing more, and at {portfolio_return*100:.2g}%/yr "
        f"it reaches the full ${nest_egg:,.0f} needed by {proj_start_year}."
    ),
)
p2.metric(
    "Your Portfolio Today",
    f"${current_portfolio:,.0f}",
    help="What you have invested right now across all accounts.",
)
if gap_today > 0:
    p3.metric(
        "Gap Today",
        f"${gap_today:,.0f}",
        help=f"You need ${nest_egg_today:,.0f} but have ${current_portfolio:,.0f} — short by ${gap_today:,.0f} in today's dollars.",
    )
else:
    p3.metric(
        "Surplus Today",
        f"${abs(gap_today):,.0f}",
        f"+${abs(gap_today):,.0f} ahead of target",
        delta_color="normal",
        help=f"Your ${current_portfolio:,.0f} already exceeds the ${nest_egg_today:,.0f} needed today.",
    )

# ── Row 2: At retirement ──
future_dollar_label = "nominal" if use_inflation else "real"
st.caption(f"**In {proj_start_year} ({future_dollar_label} dollars at {portfolio_return*100:.2g}%/yr)**")
f1, f2, f3 = st.columns(3)
f1.metric(
    f"Full Nest Egg ({proj_start_year})",
    f"${nest_egg:,.0f}",
    help=f"The nest egg target expressed in {proj_start_year} {future_dollar_label} dollars — what ${nest_egg_today:,.0f} today grows to.",
)
f2.metric(
    f"Your Portfolio ({proj_start_year})",
    f"${projected_at_retirement:,.0f}",
    help=f"What your current ${current_portfolio:,.0f} grows to by {proj_start_year} at {portfolio_return*100:.2g}%/yr.",
)
if future_gap > 0:
    f3.metric(
        f"Future Gap ({proj_start_year})",
        f"${future_gap:,.0f}",
        help=(
            f"Your portfolio (${projected_at_retirement:,.0f}) falls short of the ${nest_egg:,.0f} needed in {proj_start_year}. "
            f"This is the same gap as '${gap_today:,.0f} today' expressed in {proj_start_year} {future_dollar_label} dollars."
        ),
    )
else:
    f3.metric(
        f"Future Surplus ({proj_start_year})",
        f"${abs(future_gap):,.0f}",
        f"+${abs(future_gap):,.0f} beyond what's needed",
        delta_color="normal",
        help=f"Your portfolio (${projected_at_retirement:,.0f}) exceeds the ${nest_egg:,.0f} target in {proj_start_year}.",
    )

if gap_today > 0 and monthly_savings_to_close > 0:
    st.info(
        f"You need **${nest_egg_today:,.0f}** today but have **${current_portfolio:,.0f}** — "
        f"a gap of **${gap_today:,.0f}** in today's dollars. "
        f"To close it, contribute **${monthly_savings_to_close:,.0f}/month** between now and {proj_start_year} "
        f"({years_to_retirement} years)."
    )
elif current_portfolio == 0 and nest_egg_today > 0:
    st.info(
        f"Starting from $0, you need to save **${monthly_savings_to_close:,.0f}/month** "
        f"for {years_to_retirement} years to reach the **${nest_egg_today:,.0f}** target in today's dollars."
    )
else:
    st.success(
        f"Your current portfolio of **${current_portfolio:,.0f}** already covers the "
        f"**${nest_egg_today:,.0f}** needed today — you have a **${abs(gap_today):,.0f}** surplus. "
        f"No additional contributions required."
    )

st.markdown("---")

# Banner
if shortfall_both <= 0:
    st.success(
        f"Once both are collecting, combined OAS + CPP (${combined_both:,.0f}/mo) "
        f"**exceeds** your ${spending_monthly:,.0f}/mo spending goal — "
        f"surplus of **${abs(shortfall_both):,.0f}/mo**."
    )
else:
    coverage_pct = combined_both / spending_monthly * 100
    st.warning(
        f"Once both are collecting, combined OAS + CPP (${combined_both:,.0f}/mo) "
        f"covers **{coverage_pct:.0f}%** of your ${spending_monthly:,.0f}/mo goal. "
        f"Gap of **${shortfall_both:,.0f}/mo** to draw from savings."
    )

# ── Chart 1: Stacked income sources vs spending ──
fig_inc = go.Figure()

fig_inc.add_trace(go.Bar(
    x=df_proj["Year"], y=df_proj["P1 OAS (mo)"] * 12,
    name="Person 1 OAS", marker_color="#1e88e5",
))
fig_inc.add_trace(go.Bar(
    x=df_proj["Year"], y=df_proj["P2 OAS (mo)"] * 12,
    name="Person 2 OAS", marker_color="#64b5f6",
))
fig_inc.add_trace(go.Bar(
    x=df_proj["Year"], y=df_proj["CPP Combined (mo)"] * 12,
    name="CPP Combined", marker_color="#78909c",
))
fig_inc.add_trace(go.Scatter(
    x=df_proj["Year"], y=df_proj["Spending (mo)"] * 12,
    name="Spending Goal",
    line=dict(color="#e53935", width=2.5, dash="dash"),
    mode="lines",
))

# Retirement start marker (only if before first OAS)
if pre_oas_years > 0:
    fig_inc.add_vline(
        x=retirement_year, line_dash="dash", line_color="#e53935", line_width=2,
        annotation_text=f"Retire ({retirement_year})", annotation_position="top left",
        annotation_font_color="#e53935",
    )

# OAS start markers
fig_inc.add_vline(
    x=oas_start_year1, line_dash="dot", line_color="#1e88e5", line_width=1.5,
    annotation_text="P1 OAS", annotation_position="top left",
    annotation_font_color="#1e88e5",
)
if oas_start_year2 != oas_start_year1:
    fig_inc.add_vline(
        x=oas_start_year2, line_dash="dot", line_color="#42a5f5", line_width=1.5,
        annotation_text="P2 OAS", annotation_position="top right",
        annotation_font_color="#42a5f5",
    )

# Age-75 top-up markers
for yr_75, lbl_75 in [(birth_year1 + 75, "P1 age 75"), (birth_year2 + 75, "P2 age 75")]:
    if proj_start_year <= yr_75 <= proj_end_year:
        fig_inc.add_vline(
            x=yr_75, line_dash="dot", line_color="#4caf50", line_width=1,
            annotation_text=lbl_75, annotation_position="top right",
            annotation_font_color="#4caf50",
        )

inflation_note = f" (inflated at {inflation_rate*100:.1f}%/yr)" if use_inflation else " (today's $)"
fig_inc.update_layout(
    template="plotly_white",
    title=f"Annual Income vs Spending{inflation_note}",
    xaxis_title="Year",
    yaxis=dict(title="Annual Amount (CAD)", tickprefix="$", tickformat=",.0f"),
    barmode="stack",
    height=450,
    margin=dict(l=40, r=20, t=70, b=50),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=-0.22),
)
st.plotly_chart(fig_inc, use_container_width=True)

# ── Chart 2: Annual & cumulative shortfall ──
fig_sf = go.Figure()

fig_sf.add_trace(go.Bar(
    x=df_proj["Year"],
    y=df_proj["Annual Shortfall"],
    name="Annual Shortfall",
    marker_color=["#e53935" if s > 0 else "#43a047" for s in df_proj["Annual Shortfall"]],
    yaxis="y1",
))
fig_sf.add_trace(go.Scatter(
    x=df_proj["Year"],
    y=df_proj["Cumulative Shortfall"],
    name="Cumulative Shortfall",
    line=dict(color="#ff9800", width=2.5),
    yaxis="y2",
))

fig_sf.update_layout(
    template="plotly_white",
    title="Annual & Cumulative Shortfall",
    xaxis_title="Year",
    yaxis=dict(
        title="Annual Shortfall (CAD)", tickprefix="$", tickformat=",.0f", side="left",
    ),
    yaxis2=dict(
        title="Cumulative (CAD)", tickprefix="$", tickformat=",.0f",
        overlaying="y", side="right",
    ),
    height=380,
    margin=dict(l=40, r=70, t=50, b=50),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=-0.22),
    barmode="relative",
)
st.plotly_chart(fig_sf, use_container_width=True)

# ── Chart 3: Portfolio balance over time ──
# Split into positive and negative segments for fill colouring
pos_bal = df_proj["Portfolio Balance"].clip(lower=0)
neg_bal = df_proj["Portfolio Balance"].clip(upper=0)

fig_port = go.Figure()

# Green fill: positive balance
fig_port.add_trace(go.Scatter(
    x=df_proj["Year"], y=pos_bal,
    name="Portfolio Balance",
    fill="tozeroy",
    fillcolor="rgba(76, 175, 80, 0.15)",
    line=dict(color="#4caf50", width=2.5),
    mode="lines",
))
# Red fill: if balance goes negative (overspend scenario)
if (neg_bal < 0).any():
    fig_port.add_trace(go.Scatter(
        x=df_proj["Year"], y=neg_bal,
        name="Deficit (portfolio exhausted)",
        fill="tozeroy",
        fillcolor="rgba(229, 57, 53, 0.20)",
        line=dict(color="#e53935", width=1.5, dash="dot"),
        mode="lines",
    ))

# $0 reference line
fig_port.add_hline(y=0, line_dash="dash", line_color="#888888", line_width=1)

# Retirement start marker
if pre_oas_years > 0:
    fig_port.add_vline(
        x=retirement_year, line_dash="dash", line_color="#e53935", line_width=2,
        annotation_text=f"Retire ({retirement_year})", annotation_position="top left",
        annotation_font_color="#e53935",
    )

# OAS start markers
fig_port.add_vline(
    x=oas_start_year1, line_dash="dot", line_color="#1e88e5", line_width=1.5,
    annotation_text="P1 OAS", annotation_position="top left",
    annotation_font_color="#1e88e5",
)
if oas_start_year2 != oas_start_year1:
    fig_port.add_vline(
        x=oas_start_year2, line_dash="dot", line_color="#42a5f5", line_width=1.5,
        annotation_text="P2 OAS", annotation_position="top right",
        annotation_font_color="#42a5f5",
    )
# Age-75 top-up markers
for yr_75, lbl_75 in [(birth_year1 + 75, "P1 age 75"), (birth_year2 + 75, "P2 age 75")]:
    if proj_start_year <= yr_75 <= proj_end_year:
        fig_port.add_vline(
            x=yr_75, line_dash="dot", line_color="#4caf50", line_width=1,
            annotation_text=lbl_75, annotation_position="top right",
            annotation_font_color="#4caf50",
        )

return_note = f"{portfolio_return*100:.2g}%/yr {'nominal' if use_inflation else 'real'} return"
fig_port.update_layout(
    template="plotly_white",
    title=f"Portfolio Balance Over Time ({return_note})",
    xaxis_title="Year",
    yaxis=dict(title="Portfolio Balance (CAD)", tickprefix="$", tickformat=",.0f"),
    height=400,
    margin=dict(l=40, r=20, t=60, b=50),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=-0.22),
)
st.plotly_chart(fig_port, use_container_width=True)

# Balance at the moment the 2nd OAS starts — useful milestone
if not both_rows.empty:
    bal_at_both = df_proj.loc[df_proj["Year"] == later_start_year, "Portfolio Balance"].values
    if len(bal_at_both):
        st.caption(
            f"Portfolio balance when both OAS start ({later_start_year}): "
            f"**${bal_at_both[0]:,.0f}** — "
            + ("the portfolio is still funded at this point." if bal_at_both[0] > 0
               else "the portfolio has been exhausted before the second OAS starts.")
        )

# ── Year-by-year detail table ──
with st.expander("Year-by-Year Detail"):
    fmt = df_proj.copy()
    money_cols = [
        "P1 OAS (mo)", "P2 OAS (mo)", "CPP Combined (mo)",
        "Total Income (mo)", "Spending (mo)", "Annual Shortfall", "Cumulative Shortfall",
        "Portfolio Balance",
    ]
    for col in money_cols:
        fmt[col] = fmt[col].map("${:,.0f}".format)
    st.dataframe(fmt, use_container_width=True, hide_index=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "OAS base rate ~$727.67/month (2025 Q4, ages 65–74). Rates are CPI-indexed quarterly by the Government of Canada. "
    "CPP is assumed to start the same year as each person's OAS. "
    "Does not include the OAS clawback (income recovery tax, applies above ~$91K/year). "
    "Get your CPP projection at "
    "[My Service Canada Account](https://www.canada.ca/en/employment-social-development/services/my-account.html)."
)
