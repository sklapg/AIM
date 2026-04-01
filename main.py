import requests

HEADERS = {"User-Agent": "akash example@email.com"}



def get_cik(ticker):

    url = "https://www.sec.gov/files/company_tickers_exchange.json"
    data = requests.get(url, headers=HEADERS).json()

    ticker = ticker.upper()

    for company in data["data"]:
        if company[2] == ticker:
            return str(company[0]).zfill(10)

    return None




def get_facts(cik):

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

    return requests.get(url, headers=HEADERS).json()



def get_latest(facts, tag):

    try:
        values = facts["facts"]["us-gaap"][tag]["units"]["USD"]
        return values[-1]["val"]
    except:
        return None




def get_value(facts, tag_list):

    for tag in tag_list:

        value = get_latest(facts, tag)

        if value is not None:
            return value

    return None




def normalize_financials(facts):

    revenue = get_value(facts, [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet",
        "Revenues"
    ])

    ebit = get_value(facts, [
        "OperatingIncomeLoss"
    ])

    pretax = get_value(facts, [
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxes"
    ])

    tax_expense = get_value(facts, [
        "IncomeTaxExpenseBenefit"
    ])

    depreciation = get_value(facts, [
        "DepreciationAndAmortization",
        "DepreciationDepletionAndAmortization"
    ])

    capex = get_value(facts, [
        "PaymentsToAcquirePropertyPlantAndEquipment"
    ])

    current_assets = get_value(facts, [
        "AssetsCurrent"
    ])

    current_liabilities = get_value(facts, [
        "LiabilitiesCurrent"
    ])

    cash = get_value(facts, [
        "CashAndCashEquivalentsAtCarryingValue"
    ])

    short_term_debt = get_value(facts, [
        "DebtCurrent"
    ])

    long_term_debt = get_value(facts, [
        "LongTermDebt"
    ])

    shares = get_value(facts, [
        "CommonStockSharesOutstanding"
    ])



    working_capital = None
    if current_assets and current_liabilities:
        working_capital = current_assets - current_liabilities

    tax_rate = None
    if pretax and tax_expense:
        tax_rate = tax_expense / pretax

    total_debt = None
    if short_term_debt and long_term_debt:
        total_debt = short_term_debt + long_term_debt



    return {
        "Revenue": revenue,
        "EBIT": ebit,
        "TaxRate": tax_rate,
        "DepreciationAmortization": depreciation,
        "CapEx": capex,
        "WorkingCapital": working_capital,
        "Cash": cash,
        "Debt": total_debt,
        "SharesOutstanding": shares
    }



def main():

    ticker = input("Enter ticker: ")

    cik = get_cik(ticker)

    if cik is None:
        print("Ticker not found")
        return

    print("CIK:", cik)

    facts = get_facts(cik)

    financials = normalize_financials(facts)

    print("\nNormalized Financials\n")

    for key, value in financials.items():
        print(key, ":", value)


if __name__ == "__main__":
    main()