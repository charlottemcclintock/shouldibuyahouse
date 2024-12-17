import pandas as pd 

def calculate_monthly_mortgage_payment(loan_amount, annual_interest_rate, loan_term_years):
    """
    Calculate the monthly mortgage payment.
    This function calculates the monthly mortgage payment based on the loan amount, 
    annual interest rate, and loan term in years. It uses the formula for a fixed-rate 
    mortgage to determine the monthly payment.
    Parameters:
    loan_amount (float): The total amount of the loan.
    annual_interest_rate (float): The annual interest rate of the loan as a percentage.
    loan_term_years (int): The term of the loan in years.
    Returns:
    float: The monthly mortgage payment.
    Example:
    >>> calculate_monthly_mortgage_payment(200000, 5, 30)
    1073.64
    """

    monthly_interest_rate = annual_interest_rate / 100 / 12
    number_of_payments = loan_term_years * 12
    if monthly_interest_rate == 0:
        return loan_amount / number_of_payments
    else:
        return loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments) / ((1 + monthly_interest_rate) ** number_of_payments - 1)

def calculate_monthly_cost_buying(home_cost, monthly_payment):
    """Calculate the total monthly cost of buying a house.
    This function takes into account the monthly mortgage payment, 
    monthly repair costs, monthly property insurance, and monthly 
    homeowners insurance to compute the total monthly cost of owning a home.

    Parameters:
    home_cost (float): The total cost of the home.
    monthly_payment (float): The monthly mortgage payment.
    Returns:
    float: The total monthly cost of buying the house.
    """

    monthly_repair_cost = home_cost * 0.01 / 12
    monthly_property_insurance = home_cost * 0.009 / 12
    monthly_homeowners_insurance = 200

    total_monthly_cost_buying = monthly_payment + monthly_repair_cost + monthly_property_insurance + monthly_homeowners_insurance
    return total_monthly_cost_buying

def calculate_amortization_schedule(loan_amount, annual_interest_rate, loan_term_years, down_payment_percent, monthly_payment):
    """
    Calculate the amortization schedule for a loan.
    Parameters:
    loan_amount (float): The total amount of the loan.
    annual_interest_rate (float): The annual interest rate of the loan as a percentage.
    loan_term_years (int): The term of the loan in years.
    down_payment_percent (float): The down payment as a percentage of the total home value.
    monthly_payment (float): The fixed monthly payment amount.
    Returns:
    pd.DataFrame: A DataFrame containing the amortization schedule with columns:
        - Year: The year of the payment.
        - Month: The month of the payment.
        - Payment Number: The sequential number of the payment.
        - Principal Payment: The portion of the payment that goes towards the principal.
        - Interest Payment: The portion of the payment that goes towards interest.
        - Remaining Balance: The remaining balance of the loan after the payment.
        - Equity (%): The percentage of the home value that is owned (equity).
    """

    monthly_interest_rate = annual_interest_rate / 100 / 12
    number_of_payments = loan_term_years * 12
    schedule = []

    remaining_balance = loan_amount
    total_home_value = loan_amount / (1 - down_payment_percent / 100)
    equity = total_home_value * (down_payment_percent / 100)

    for payment_number in range(1, number_of_payments + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        equity += principal_payment
        equity_percent = (equity / total_home_value) * 100
        year = (payment_number - 1) // 12 + 1
        month = (payment_number - 1) % 12 + 1
        schedule.append({
            "Year": year,
            "Month": month,
            "Payment Number": payment_number,
            "Principal Payment": round(principal_payment),
            "Interest Payment": round(interest_payment),
            "Remaining Balance": round(remaining_balance),
            "Equity (%)": round(equity_percent, 2)
        })

    return pd.DataFrame(schedule)

def calculate_summary_metrics(down_payment, home_cost, interest_rate, loan_term_years, home_price_appreciation, inflation, investment_growth, closing_costs, rent, rent_increase, amortization_schedule, monthly_payment, total_monthly_cost_buying):
    """
    Calculate and summarize various financial metrics for buying vs renting a home over a specified loan term.

    Parameters:
    down_payment (float): The down payment percentage for the home.
    home_cost (float): The initial cost of the home.
    interest_rate (float): The annual interest rate of the mortgage.
    loan_term_years (int): The duration of the loan in years.
    home_price_appreciation (float): The annual appreciation rate of the home value.
    inflation (float): The annual inflation rate.
    investment_growth (float): The annual growth rate of investments.
    closing_costs (float): The closing costs as a percentage of the home cost.
    rent (float): The initial monthly rent.
    rent_increase (float): The annual increase rate of rent.
    amortization_schedule (pd.DataFrame): The amortization schedule of the mortgage.
    monthly_payment (float): The monthly mortgage payment.
    total_monthly_cost_buying (float): The total monthly cost of buying the home.

    Returns:
    pd.DataFrame: A DataFrame containing the summary of financial metrics for each year.
    """

    summary_data = {
        "Year": [],
        "Annual Cost of Buying": [],
        "Equity in Home": [],
        "Home Value": [],
        "Investment: Buy": [],
        "Annual Cost of Renting": [],
        "Cost Savings": [],
        "Investment: Rent": [],
        "Investment: Rent + Re-invest": []
    }

    total_investment_value_rent_reinvest = down_payment / 100 * home_cost

    for year in range(1, loan_term_years + 1):
        total_home_value = home_cost * (1 + (home_price_appreciation + inflation) / 100) ** year

        equity_percent = amortization_schedule[amortization_schedule["Year"] == year]["Equity (%)"].iloc[-1] 
        total_investment_value_home = equity_percent / 100 * total_home_value 
        total_annual_cost_buying = total_monthly_cost_buying * 12
        if year == 1:
            total_annual_cost_buying += closing_costs / 100 * home_cost
        total_investment_value_rent = down_payment / 100 * home_cost * (1 + (investment_growth + inflation)/ 100) ** year
        total_annual_cost_renting = rent * 12 * (1 + (rent_increase + inflation) / 100) ** (year)
        annual_savings_housing_costs =  total_annual_cost_buying - total_annual_cost_renting

        total_investment_value_rent_reinvest = (total_investment_value_rent_reinvest  * (1 + (investment_growth + inflation) / 100)) + annual_savings_housing_costs

        summary_data["Year"].append(year)
        summary_data["Annual Cost of Buying"].append(round(total_annual_cost_buying))
        summary_data["Equity in Home"].append(round(equity_percent))
        summary_data["Home Value"].append(round(total_home_value))
        summary_data["Investment: Buy"].append(round(total_investment_value_home))
        summary_data["Annual Cost of Renting"].append(round(total_annual_cost_renting))
        summary_data["Cost Savings"].append(round(annual_savings_housing_costs))
        summary_data["Investment: Rent"].append(round(total_investment_value_rent))
        summary_data["Investment: Rent + Re-invest"].append(round(total_investment_value_rent_reinvest))

    summary_df = pd.DataFrame(summary_data)

    return summary_df