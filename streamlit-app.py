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
st.set_page_config(layout="wide", page_title="Should I Buy a House?")

# apply styling defined in style.css
apply_custom_css(custom_css)


# ................................ BEGIN APP STRUCTURE.................................


with st.sidebar:
    st.markdown("## Should I Buy a House?")
    st.caption('''I live in a high cost of living area and kept feeling like I *should* buy a house at some point, that it was better than "throwing money away" by renting. Here's my math on when that makes sense. ''')


    st.markdown(" ")


    with st.container(border=True):
        st.markdown("**Buy**")

        subcol1, subcol2 = st.columns(2)
        with subcol1:
            home_cost = st.number_input("Home Price ($)", value=800000, step=10000, )
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
            rent_increase = st.number_input("Rent Increase (%)", min_value=0.0, max_value=100.0, format="%.1f", value=1.0, step = 0.5, help="Annual rent increase after inflation.")
    with st.expander("Advanced Options"): 
        st.markdown("**Macro**")
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            inflation = st.number_input("Inflation Rate (%)", min_value=0.0, max_value=100.0, format="%.1f", value=3.0, step=0.5)
            home_price_appreciation = st.number_input("Home Price Appreciation After Inflation (%)", min_value=0.0, max_value=100.0, format="%.1f", value=1.0, step=0.5)
        with subcol2:
            loan_term_years = st.number_input("Loan Term (years)", step=5, value=30, min_value=15)  # Assuming a 30-year mortgage
            investment_growth = st.number_input("Average Investment Growth (%)", min_value=0.0, max_value=100.0, format="%.1f", value=5.0, step = 0.5, help="Average annual return on investment portfolio after inflation.")

    st.caption('Note: I built this one afternoon - please flag any bugs or issues! Send all thoughts and feedback to [Charlotte](https://bsky.app/profile/cmcclintock.bsky.social)!')
 


# Example usage
loan_amount = home_cost * (1 - down_payment / 100)
monthly_payment = calculate_monthly_mortgage_payment(loan_amount, interest_rate, loan_term_years)

total_monthly_cost_buying = calculate_monthly_cost_buying(home_cost, monthly_payment)

# Calculate amortization schedule
amortization_schedule = calculate_amortization_schedule(loan_amount, interest_rate, loan_term_years, down_payment, monthly_payment)

summary_df = calculate_summary_metrics(down_payment, home_cost, interest_rate, loan_term_years, home_price_appreciation, inflation, investment_growth, closing_costs, rent, rent_increase)

tab1, tab2 = st.tabs(["big picture", "cost breakdown"])

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
                "scenarios",
                options=["Buy", "Rent", "Rent + Invest"],
                default=["Buy", "Rent", "Rent + Invest"]
            )

    with investment_graph:

        # filter the summary dataframe based on the selected year range
        filtered_summary_df = summary_df[(summary_df["Year"] >= year_slider[0]) & (summary_df["Year"] <= year_slider[1])]

        # melt the dataframe
        filtered_chart_data = filtered_summary_df.melt(id_vars=["Year"], value_vars=["Investment: Buy", "Investment: Rent", "Investment: Rent + Invest"], var_name="Type", value_name="Investment")

        # clean up the investment types
        filtered_chart_data['Type'] = filtered_chart_data['Type'].str.replace("Investment: ", "")

        # subset the chart data based on the selected scenarios
        filtered_chart_data = filtered_chart_data[filtered_chart_data['Type'].isin(scenarios)]

        # set up the altair chart
        filtered_investment_chart = alt.Chart(filtered_chart_data).mark_line(point=True).encode(
            x=alt.X('Year:Q', title=''),
            y=alt.Y('Investment:Q', title='', axis=alt.Axis(format='$,.0f')),
            color=alt.Color('Type:N', title='Type', scale=alt.Scale(domain=['Buy', 'Rent', 'Rent + Invest'], range=['#E76C7E', '#D7D46D', '#406F0F'])),
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
            "Type:N", legend=None, scale=alt.Scale(domain=['Buy', 'Rent', 'Rent + Invest'], range=['#ffa600', '#d45087', '#a05195'])
            )
            )
        )

        st.altair_chart(filtered_investment_chart + filtered_labels, use_container_width=True)
    

    st.markdown("**Detailed Breakdown**")
    st.markdown(f"This scenario compares buying a home at **\\${home_cost:,}** with a **{down_payment}%** down payment to renting a home at **\\${rent:,}** per month.")
    st.markdown(f"*If you bought this house:* You would pay **\\${total_monthly_cost_buying*12:,.0f}** per year, including the mortgage payment, repair costs, property insurance, and homeowners insurance. In year one, you'd also pay **\\${closing_costs/100*home_cost:,.0f}** in closing costs. Your costs would be fixed for **{loan_term_years}** years. After 30 years, you would own **100%** of the home, which would be worth **\\${max(summary_df['Investment: Buy']):,.0f}**, based on **{home_price_appreciation}%** annual appreciation in the value of the home and **{inflation}%** inflation.")

    st.markdown(f"*If you rented this house:* You would pay **\\${min(summary_df['Annual Cost of Renting']):,.0f}** in the first year and **\\${max(summary_df['Annual Cost of Renting']):,.0f}** in year 30, with rent increasing by **{rent_increase}%** annually on top of **{inflation}%** inflation. Your costs would increase with inflation. You would not own the home, but you would have invested the **\\${(down_payment + closing_costs)/100*home_cost:,.0f}** you would have spent on a down payment and closing costs, which would be worth **\\${max(summary_df['Investment: Rent']):,.0f}** after **{loan_term_years}** years, based on an average annual return of **{investment_growth}%** after inflation.")

    st.markdown(f"*If you rented this house and invested the cost savings:* You would pay **\\${min(summary_df['Annual Cost of Renting']):,.0f}** in the first year and **\\${max(summary_df['Annual Cost of Renting']):,.0f}** in year 30, with rent increasing by **{rent_increase}%** annually on top of **{inflation}%** inflation. Your costs would increase with inflation. You would not own the home, but you would have invested the down payment and closing costs (**\\${(down_payment + closing_costs)/100*home_cost:,.0f}**) in the stock market *plus* you would invest the cost difference between buying and renting each year (**\${summary_df['Cost Savings'].values[0]:,.0f}** in year 1), which would be worth **\\${max(summary_df['Investment: Rent + Invest']):,.0f}** after **{loan_term_years}** years, based on an average annual return of **{investment_growth}%** after inflation.")


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
            "Investment: Rent + Invest": "${:,.0f}"
        })
        .applymap(lambda x: 'color: #E76C7E', subset=["Investment: Buy"])
        .applymap(lambda x: 'color: #D7D46D', subset=["Investment: Rent"])
        .applymap(lambda x: 'color: #406F0F', subset=["Investment: Rent + Invest"])
    )


    st.dataframe(format_df, height=220)

    st.divider()
    # iterate over home prices to find the max price where buying is better than renting and investing
    df_list = []
    for potential_home_price in range(100000, 2000000, 10000):
        potential_summary_df = calculate_summary_metrics(down_payment, potential_home_price, interest_rate, loan_term_years, home_price_appreciation, inflation, investment_growth, closing_costs, rent, rent_increase)
        potential_summary_df['scenario_home_price'] = potential_home_price
        potential_summary_df = potential_summary_df[potential_summary_df["Year"] == loan_term_years]
        df_list.append(potential_summary_df[['scenario_home_price', 'Investment: Buy', 'Investment: Rent', 'Investment: Rent + Invest']])

    max_price_buy_better = pd.concat(df_list)

    # Find the first scenario home price where investment buy > investment rent and invest
    first_scenario = max_price_buy_better[max_price_buy_better['Investment: Buy'] < max_price_buy_better['Investment: Rent + Invest']].iloc[0]

    # Melt the max price dataframe to long format for the chart
    max_price_buy_better_long = max_price_buy_better.melt(id_vars=['scenario_home_price'], value_vars=['Investment: Buy', 'Investment: Rent', 'Investment: Rent + Invest'], var_name='Type', value_name='Investment')

    # remove investment: from typ
    max_price_buy_better_long['Type'] = max_price_buy_better_long['Type'].str.replace("Investment: ", "")

    homepricecol1, homepricecol2 = st.columns([3,5])
    with homepricecol1:
        st.markdown("**Max Home Price where Buying > Renting**")
        st.markdown(f"The home price maximum below is the highest home price (given the input parameters) where the total investment value of buying a home exceeds renting and investing over {loan_term_years} years.  ")

        st.metric('Max Home Price Where Buying > Renting', f"${first_scenario['scenario_home_price']:,.0f}")

        st.markdown("The chart at right shows the total investment value of buying, renting, and renting + investing for a range of home prices. ")

    with homepricecol2: 
        # Graph the max price dataframe
        max_price_chart = alt.Chart(max_price_buy_better_long).mark_line(point=True).encode(
            x=alt.X('scenario_home_price:Q', title='Home Price ($)', axis=alt.Axis(format='$,.0f')),
            y=alt.Y('Investment:Q', title='Investment Value ($)', axis=alt.Axis(format='$,.0f')),
            color=alt.Color('Type:N', title='scenario', scale=alt.Scale(domain=['Buy', 'Rent', 'Rent + Invest'], range=['#E76C7E', '#D7D46D', '#406F0F'])),
            tooltip=[
                alt.Tooltip('scenario_home_price:Q', title='Home Price ($)', format='$,.0f'),
                alt.Tooltip('Investment:Q', title='Investment Value ($)', format='$,.0f'),
                alt.Tooltip('Type:N', title='Scenario')
            ]
        ).properties(
            title="Investment Value by Home Price",
            height=500,
        )

        labels = (
            alt.Chart(max_price_buy_better_long)
            .mark_text(align="left", baseline="middle", dx=5, dy=0)
            .encode(
            alt.X("scenario_home_price:Q", aggregate="max"),
            alt.Y("Investment:Q", aggregate="max"),
            alt.Text("Type:N"),
            alt.Color(
            "Type:N", legend=None, scale=alt.Scale(domain=['Buy', 'Rent', 'Rent + Invest'], range=['#ffa600', '#d45087', '#a05195'])
            )
            )
        )

        st.altair_chart(max_price_chart + labels, use_container_width=True)


with tab2:
    
    st.markdown(" ")

    # create an altair line chart for interest vs principal payments
    interest_vs_principal_chart_data = amortization_schedule.melt(id_vars=["Payment Number", "Year", "Month"], value_vars=["Principal Payment", "Interest Payment"], var_name="Type", value_name="Amount")





    # Calculate total amount paid, principal paid, and interest paid
    total_paid = amortization_schedule["Principal Payment"].sum() + amortization_schedule["Interest Payment"].sum()
    total_principal_paid = amortization_schedule["Principal Payment"].sum()
    total_interest_paid = amortization_schedule["Interest Payment"].sum()
    # Calculate down payment amount
    down_payment_amount = home_cost * (down_payment / 100)

    st.markdown("**Purchase & Mortgage Costs**")
    # Display metrics in four columns
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Down Payment Amount", value=f"${down_payment_amount:,.0f}")
    with col2:
        # closing costs
        st.metric(label="Closing Costs", value=f"${closing_costs/100*home_cost:,.0f}")
    with col3:
        st.metric(label="Mortgage Amount", value=f"${home_cost-down_payment_amount:,.0f}")
    with col4:
        st.metric(label="Total Paid on Loan", value=f"${total_paid:,.0f}", help="Total principal and interest paid over the life of the loan, does not include down payment or closing costs.")

    with col5:
        st.metric(label="Total Interest Paid", value=f"${total_interest_paid:,.0f}")

    st.markdown(" ")

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
        title="Amortization Schedule",
        height=500,
    )

    st.altair_chart(interest_vs_principal_chart, use_container_width=True)

    st.divider()

    # Calculate monthly maintenance, insurance, and property tax costs
    total_monthly_cost_buying, monthly_repair_cost, monthly_property_tax, monthly_property_insurance  = calculate_monthly_cost_buying(home_cost, monthly_payment, extended=True)
    st.markdown("**Monthly Costs**")
    col0, col1, col2, col3, col4 = st.columns(5)
    with col0:
        st.metric(label="Total Monthly Cost", value=f"${total_monthly_cost_buying:,.0f}")
    with col1:
        st.metric(label="Mortgage Payment", value=f"${monthly_payment:,.0f}")
    with col2:
        st.metric(label="Maintenance", value=f"${monthly_repair_cost:,.0f}", help="1% of the home value annually set aside for repairs")
    with col3:
        st.metric(label="Insurance", value=f"${monthly_property_insurance:,.0f}")
    with col4:
        st.metric(label="Property Tax", value=f"${monthly_property_tax:,.0f}", help="Based on Seattle, WA property tax - 0.9% of the home value annually ([SmartAsset](https://smartasset.com/taxes/washington-property-tax-calculator#bx0Z9LHuTc)).")