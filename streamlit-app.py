import streamlit as st 
import altair as alt 
import pandas as pd
from utils import *

# ................................ SET UP .................................

# Set up Altair theme
def altair_theme():
    return {
        'config': {
            'title': {'font': 'Inter'},
            'axis': {
                'labelFont': 'Inter',
                'titleFont': 'Inter',
            },
            'legend': {'labelFont': 'Inter', 'titleFont': 'Inter'}
        }
    }

# Register the theme
alt.themes.register('custom_theme', altair_theme)
alt.themes.enable('custom_theme')


# set up custom css styling
with open("style.css") as css:
    custom_css = css.read()


# markdown -> html to apply custom css
def apply_custom_css(css):
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# use full width of page
st.set_page_config(layout="wide")

# apply styling defined in style.css
apply_custom_css(custom_css)


# ................................ BEGIN APP STRUCTURE.................................


with st.sidebar:
    st.markdown("## Should I Buy a House?")
    st.caption('''I live in a high cost of living area and kept feeling like I *should* buy a house at some point, that it was better than "throwing money away" by renting. Here's my math on when that makes sense. ''')
    st.markdown("#")

    with st.container(border=True):
        st.markdown("**Buy**")

        subcol1, subcol2 = st.columns(2)
        with subcol1:
            home_cost = st.number_input("Home Purchase Price ($)", value=800000, step=10000, )
            interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=100.0, format="%.1f", value=7.0, step=0.5)
        with subcol2:
            down_payment = st.number_input("Down Payment (%)", min_value=0, max_value=100,  value=20, step=1)
            closing_costs = st.number_input("Closing Costs (%)", min_value=0.0, max_value=100.0, format="%.1f", value=3.0, step=0.5)
    with st.container(border=True):
        st.markdown("**Rent**")
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            rent = st.number_input("Monthly Rent ($)", value=2500, step = 100)
        with subcol2:
            rent_increase = st.number_input("Rent Increase after Inflation (%)", min_value=0.0, max_value=100.0, format="%.1f", value=1.0, step = 0.5)
    with st.expander("Advanced Options"): 
        st.markdown("**Macro**")
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            inflation = st.number_input("Inflation Rate (%)", min_value=0.0, max_value=100.0, format="%.1f", value=3.0, step=0.5)
            home_price_appreciation = st.number_input("Home Price Appreciation After Inflation (%)", min_value=0.0, max_value=100.0, format="%.1f", value=1.0, step=0.5)
        with subcol2:
            investment_growth = st.number_input("Average Investment Growth (%)", min_value=0.0, max_value=100.0, format="%.1f", value=7.0, step = 0.5, help="Average annual return on investment portfolio after inflation.")
            loan_term_years = st.number_input("Loan Term (years)", step=5, value=30, min_value=15)  # Assuming a 30-year mortgage


# Example usage
loan_amount = home_cost * (1 - down_payment / 100)
monthly_payment = calculate_monthly_mortgage_payment(loan_amount, interest_rate, loan_term_years)

total_monthly_cost_buying = calculate_monthly_cost_buying(home_cost, monthly_payment)

# Calculate amortization schedule
amortization_schedule = calculate_amortization_schedule(loan_amount, interest_rate, loan_term_years, down_payment, monthly_payment)

summary_df = calculate_summary_metrics(down_payment, home_cost, interest_rate, loan_term_years, home_price_appreciation, inflation, investment_growth, closing_costs, rent, rent_increase, amortization_schedule, monthly_payment, total_monthly_cost_buying)

tab1, tab2 = st.tabs(["big picture", "amortization schedule"])

with tab1:

    # add a spacer
    st.markdown(" ")

    # set up columns in first row
    toplines, investment_graph = st.columns([1.25, 6], gap="medium")

    with toplines:
        st.markdown("**Toplines**")

        # topline metrics
        st.metric(label="Monthly Cost of Renting", value=f"${rent:,.0f}")
        st.metric(label = f"Monthly Mortgage Payment", value=f"${monthly_payment:,.0f}")
        st.metric(label="Monthly Cost of Buying", value=f"${total_monthly_cost_buying:,.0f}", help = "Includes mortgage payment, repair costs, property insurance, and homeowners insurance.")

        # graph options
        with st.expander("graph options"):
            # Add a time slider to filter the chart
            year_slider = st.slider("zoom in on years", min_value=1, max_value=30, value=(1, 30))
            scenarios = st.multiselect(
                "Select Scenarios to Display",
                options=["Buy", "Rent", "Rent + Re-invest"],
                default=["Buy", "Rent", "Rent + Re-invest"]
            )

    with investment_graph:

        # filter the summary dataframe based on the selected year range
        filtered_summary_df = summary_df[(summary_df["Year"] >= year_slider[0]) & (summary_df["Year"] <= year_slider[1])]

        # melt the dataframe
        filtered_chart_data = filtered_summary_df.melt(id_vars=["Year"], value_vars=["Investment: Buy", "Investment: Rent", "Investment: Rent + Re-invest"], var_name="Type", value_name="Investment")

        # clean up the investment types
        filtered_chart_data['Type'] = filtered_chart_data['Type'].str.replace("Investment: ", "")

        # subset the chart data based on the selected scenarios
        filtered_chart_data = filtered_chart_data[filtered_chart_data['Type'].isin(scenarios)]

        # set up the altair chart
        filtered_investment_chart = alt.Chart(filtered_chart_data).mark_line(point=True).encode(
            x=alt.X('Year:Q', title=''),
            y=alt.Y('Investment:Q', title='', axis=alt.Axis(format='$,.0f')),
            color=alt.Color('Type:N', title='Type', scale=alt.Scale(domain=['Buy', 'Rent', 'Rent + Re-invest'], range=['#E76C7E', '#D7D46D', '#406F0F'])),
            tooltip=[
            alt.Tooltip('Year:Q', title='Year'),
            alt.Tooltip('Investment:Q', title='Value ($)', format='$,.0f'),
            alt.Tooltip('Type:N', title='Scenario')
            ]
        ).properties(
            title={
            "text": "Investment Value"
            },
            height=500,
        )

        # add labels to the chart
        filtered_labels = (
            alt.Chart(filtered_chart_data)
            .mark_text(align="left", baseline="middle", dx=5, dy=0)
            .encode(
            alt.X("Year:Q", aggregate="max"),
            alt.Y("Investment:Q", aggregate="max"),
            alt.Text("Type:N"),
            alt.Color(
            "Type:N", legend=None, scale=alt.Scale(domain=['Buy', 'Rent', 'Rent + Re-invest'], range=['#ffa600', '#d45087', '#a05195'])
            )
            )
        )

        st.altair_chart(filtered_investment_chart + filtered_labels, use_container_width=True)
    

    st.markdown("**Detailed Breakdown**")
    st.markdown(f"This scenario compares buying a home at **\\${home_cost:,}** with a **{down_payment}%** down payment to renting a home at **\\${rent:,}** per month.")
    st.markdown(f"*If you bought this house:* You would pay **\\${total_monthly_cost_buying*12:,.0f}** per year, including the mortgage payment, repair costs, property insurance, and homeowners insurance. In year one, you'd also pay **\\${closing_costs/100*home_cost:,.0f}** in closing costs. Your costs would be fixed for **{loan_term_years}** years. After 30 years, you would own **100%** of the home, which would be worth **\\${max(summary_df['Investment: Buy']):,.0f}**, based on **{home_price_appreciation}%** annual appreciation in the value of the home and **{inflation}%** inflation.")

    st.markdown(f"*If you rented this house:* You would pay **\\${min(summary_df['Annual Cost of Renting']):,.0f}** in the first year and **\\${max(summary_df['Annual Cost of Renting']):,.0f}** in year 30, with rent increasing by **{rent_increase}%** annually on top of **{inflation}%** inflation. Your costs would increase with inflation. You would not own the home, but you would have **{down_payment}%** of the home value invested in the stock market, which would be worth **\\${max(summary_df['Investment: Rent']):,.0f}** after **{loan_term_years}** years, based on an average annual return of **{investment_growth}%** after inflation.")

    st.markdown(f"*If you rented this house and reinvested the cost savings:* You would pay **\\${min(summary_df['Annual Cost of Renting']):,.0f}** in the first year and **\\${max(summary_df['Annual Cost of Renting']):,.0f}** in year 30, with rent increasing by **{rent_increase}%** annually on top of **{inflation}%** inflation. Your costs would increase with inflation. You would not own the home, but you would have **{down_payment}%** of the home value invested in the stock market, which would be worth **\\${max(summary_df['Investment: Rent + Re-invest']):,.0f}** after **{loan_term_years}** years, based on an average annual return of **{investment_growth}%** after inflation.")


    # display the summary dataframe
    format_df = summary_df.copy()
    format_df.set_index('Year', inplace=True)

    format_df = (format_df.style
        .format({
            "Year": "{:.0f}",
            "Equity in Home": "{:.0f}%",
            "Home Value": "${:,.0f}",
            "Investment: Buy": "${:,.0f}",
            "Annual Cost of Buying": "${:,.0f}",
            "Investment: Rent": "${:,.0f}",
            "Annual Cost of Renting": "${:,.0f}",
            "Cost Savings": "${:,.0f}",
            "Investment: Rent + Re-invest": "${:,.0f}"
        })
        .applymap(lambda x: 'color: #E76C7E', subset=["Investment: Buy"])
        .applymap(lambda x: 'color: #D7D46D', subset=["Investment: Rent"])
        .applymap(lambda x: 'color: #406F0F', subset=["Investment: Rent + Re-invest"])
    )

    st.dataframe(format_df)

with tab2:
    
    st.markdown("**Amortization Schedule**")

    # create an altair line chart for interest vs principal payments
    interest_vs_principal_chart_data = amortization_schedule.melt(id_vars=["Payment Number", "Year", "Month"], value_vars=["Principal Payment", "Interest Payment"], var_name="Type", value_name="Amount")

    interest_vs_principal_chart = alt.Chart(interest_vs_principal_chart_data).mark_line(point=True).encode(
        x='Payment Number:Q',
        y='Amount:Q',
        color=alt.Color('Type:N', scale=alt.Scale(domain=['Principal Payment', 'Interest Payment'], range=['#D7D46D', '#E76C7E'])),
        tooltip=[
            alt.Tooltip('Payment Number:Q', title='Payment Number'),
            alt.Tooltip('Amount:Q', title='Amount ($)', format='$,.0f'),
            alt.Tooltip('Type:N', title='Type')
        ]
    ).properties(
        title="Interest vs Principal Payments",
        height=500,
    )

    st.altair_chart(interest_vs_principal_chart, use_container_width=True)

    # set year and month as multiindex 
    amortization_schedule.set_index(['Year', 'Month'], inplace=True)

    # display the amortization schedule
    st.dataframe(amortization_schedule[['Principal Payment', 'Interest Payment', 'Remaining Balance', 'Equity (%)']])
