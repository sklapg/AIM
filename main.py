import requests

HEADERS = {"User-Agent": "YourName example@email.com"}

def get_cik(ticker):
    url = "https://www.sec.gov/files/company_tickers_exchange.json"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return None

    ticker = ticker.upper()
    for company in data["data"]:
        if company[2] == ticker:
            return str(company[0]).zfill(10)
    return None

def get_facts(cik):
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def get_latest(facts, tag, unit="USD"):
    try:
        namespaces = ["us-gaap", "dei"]
        for ns in namespaces:
            if ns in facts["facts"] and tag in facts["facts"][ns]:
                values = facts["facts"][ns][tag]["units"][unit]
                return values[-1]["val"]
    except (KeyError, IndexError):
        return None
    return None

def get_value(facts, tag_list, unit="USD"):
    for tag in tag_list:
        value = get_latest(facts, tag, unit)
        if value is not None:
            return value
    return None

def normalize_financials(facts):
    revenue = get_value(facts, ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", "Revenues"])
    ebit = get_value(facts, ["OperatingIncomeLoss"])
    pretax = get_value(facts, ["IncomeLossFromContinuingOperationsBeforeIncomeTaxes"])
    tax_expense = get_value(facts, ["IncomeTaxExpenseBenefit"])
    
    depreciation = get_value(facts, ["DepreciationAndAmortization", "DepreciationDepletionAndAmortization"])
    capex = get_value(facts, ["PaymentsToAcquirePropertyPlantAndEquipment"])
    
    current_assets = get_value(facts, ["AssetsCurrent"])
    current_liabilities = get_value(facts, ["LiabilitiesCurrent"])
    cash = get_value(facts, ["CashAndCashEquivalentsAtCarryingValue"])
    
    short_term_debt = get_value(facts, ["DebtCurrent"]) or 0
    long_term_debt = get_value(facts, ["LongTermDebt", "LongTermDebtNoncurrent"]) or 0
    
    shares = get_value(facts, ["CommonStockSharesOutstanding", "EntityCommonStockSharesOutstanding"], unit="shares")

    working_capital = None
    if current_assets and current_liabilities:
        working_capital = current_assets - current_liabilities

    tax_rate = None
    if pretax and tax_expense and pretax > 0:
        tax_rate = tax_expense / pretax
    
    total_debt = short_term_debt + long_term_debt

    return {
        "Revenue": revenue,
        "EBIT": ebit,
        "Tax Rate (%)": round(tax_rate * 100, 2) if tax_rate else None,
        "Depreciation & Amortization": depreciation,
        "CapEx": capex,
        "Working Capital": working_capital,
        "Cash": cash,
        "Total Debt": total_debt,
        "Shares Outstanding": shares
    }

def main():
    ticker = input("Enter ticker: ").strip().upper()
    cik = get_cik(ticker)

    if cik is None:
        print("Ticker not found")
        return

    facts = get_facts(cik)
    if not facts:
        return

    financials = normalize_financials(facts)

    print(f"\n--- Financials: {ticker} ---")
    for key, value in financials.items():
        if value is None:
            print(f"{key}: N/A")
        elif isinstance(value, (int, float)):
            print(f"{key}: {value:,}")
        else:
            print(f"{key}: {value}")

if __name__ == "__main__":
    main()