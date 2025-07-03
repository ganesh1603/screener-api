from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "<h3>✅ Screener Scraper Running</h3>"

@app.route("/screener", methods=["POST"])
def screener():
    try:
        data = request.json
        stock = data.get("stock", "").upper()
        if not stock:
            return jsonify({"error": "Company not found"})

        url = f"https://www.screener.in/company/{stock}/consolidated/"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")

        ratios = soup.select("li.flex.flex-space-between b")

        company_url = f"https://www.screener.in/company/{stock}/"

        screener_data = {
            "Stock": stock,
            "ROE": ratios[1].text if len(ratios) > 1 else "",
            "Debt to Equity": ratios[2].text if len(ratios) > 2 else "",
            "Current Ratio": ratios[3].text if len(ratios) > 3 else "",
            "Market Cap": ratios[4].text if len(ratios) > 4 else "",
            "Price to Earnings": ratios[5].text if len(ratios) > 5 else "",
            "Price to Book": ratios[6].text if len(ratios) > 6 else "",
            "Dividend Yield": ratios[7].text if len(ratios) > 7 else "",
            "52 Week High": ratios[8].text if len(ratios) > 8 else "",
            "52 Week Low": ratios[9].text if len(ratios) > 9 else "",
            "Concall URL": company_url + "concall/"
        }

        # Prepare unified prompt for Gemini
        prompt = f"""
You are a multi-disciplinary financial expert with deep experience in fundamental research, technical analysis, forensic accounting, and valuation modeling. I am providing you with multiple inputs related to a specific company including its annual report, earnings call transcript, credit rating report, investor presentation, financial data (balance sheet, income statement, cash flows), and a price chart.

Your task is to conduct a thorough and well-rounded company analysis using the four core dimensions below.

Company Screener Data:
{company_data}

---

1. Fundamental Research
You are a senior financial analyst with expertise in fundamental research and company valuation. Your task is to conduct a thorough fundamental analysis of this company by systematically examining all provided materials and extracting key insights. Please organize your analysis into the following sections:

- Executive Summary (Brief overview of the company and key findings)
- Business Model Analysis (Core operations, revenue streams, competitive advantages)
- Financial Performance (Revenue trends, profitability metrics, cash flow analysis)
- Balance Sheet Strength (Debt levels, liquidity ratios, capital allocation)
- Growth Outlook (Projected expansion, new markets/products, management guidance)
- Risk Assessment (Industry challenges, company-specific concerns, credit rating factors)
- Valuation Perspective (Current multiples compared to historical/peers, fair value estimate)

For each section, cite specific data points from the provided documents to support your analysis. Highlight any contradictions or discrepancies between different sources. When providing financial metrics, include both the raw numbers and your interpretation of what they indicate about the company's health. Maintain a balanced, objective tone throughout your analysis — acknowledge both strengths and weaknesses. Be precise in your language and avoid vague statements like "the company is performing well" without supporting evidence.

---

2. Technical Research
You are an expert technical analyst with extensive experience in chart pattern recognition, indicator analysis, and market forecasting. I am providing you with a price chart for analysis. Your task is to perform a detailed technical analysis of this chart, identifying key patterns, trends, and potential trading opportunities. Please structure your analysis as follows:

- Chart Overview (Timeframe, asset class, current price action context)
- Trend Analysis (Primary and secondary trends, support/resistance levels with specific price points)
- Key Pattern Identification (Chart patterns like head and shoulders, triangles, flags with completion targets)
- Technical Indicator Insights (Analysis of visible indicators such as RSI, MACD, Bollinger Bands, etc.)
- Volume Analysis (Volume trends and their confirmation/divergence from price action)
- Key Price Levels (Critical support/resistance zones, pivot points, with specific numerical values)
- Trading Opportunities (Potential entry points, stop-loss levels, and price targets with risk/reward ratios)
- Time Projections (When significant moves might occur based on pattern completion)

Base your analysis strictly on what you can observe in the provided chart. Include specific price levels, indicator readings, and pattern measurements whenever possible. Maintain a confident but measured tone — clearly differentiate between high-probability setups and speculative possibilities.

---

3. Fraud Check / Forensic Audit
You are a forensic accounting specialist with expertise in detecting financial fraud, accounting irregularities, and earnings manipulation. Your task is to conduct a detailed fraud check, examining the financial statements and disclosures for potential red flags. Please organize your analysis as follows:

- Executive Summary (Brief overview of your key findings and risk assessment)
- Revenue Recognition Analysis (Unusual patterns, premature recognition, channel stuffing)
- Expense and Liability Assessment (Suspicious capitalization, hidden liabilities, unusual deferrals)
- Cash Flow Discrepancies (Divergence between earnings and cash flow, unusual reconciliation items)
- Balance Sheet Examination (Asset quality issues, inventory concerns, receivables aging)
- Footnote and Disclosure Review (Accounting policy changes, related party transactions, litigation)
- Management Discussion Analysis (Inconsistencies with financial data, changing narratives, warning signs)
- Financial Ratio Analysis (Deteriorating metrics, industry outliers, year-over-year anomalies)
- Related Party Transactions (Details of suspicious related party transactions)

Quote specific language and page numbers where applicable. Rate the severity (Low/Medium/High). Avoid speculation — base your analysis strictly on data.

---

4. Valuation Modeling (DCF)
You are an elite investment banker and financial modeling expert specializing in DCF valuations. Please structure your valuation as follows:

- Company Overview (Brief summary based on available financial data)
- Historical Financial Analysis:
    - Revenue CAGR
    - Margin analysis (gross, operating, EBITDA, net)
    - Cash conversion cycle, leverage ratios (Debt/EBITDA, interest coverage), ROE/ROIC
- DCF Model Assumptions:
    - Revenue growth forecast
    - Margin evolution
    - CapEx, working capital needs
    - Depreciation/amortization, tax rate assumptions
- DCF Valuation:
    - Forecast period (5–10 years)
    - Terminal value (perpetuity & exit multiple)
    - WACC assumptions
    - Enterprise to equity bridge, per-share value
- Sensitivity Tables (WACC vs growth/multiples)
- Valuation Commentary (drivers, risks, capital structure, funding needs)

Include clear numeric projections and explain all assumptions.

---
"""

        # Send to Gemini API
        gemini_api_key = "AIzaSyAwKJUNTk6wZpWbFvQif1CSYlN5INOoXfA"
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_api_key}"
        headers = {"Content-Type": "application/json"}
        body = {"contents": [{"parts": [{"text": prompt}]}]}

        gemini_response = requests.post(gemini_url, headers=headers, json=body)
        reply = gemini_response.json()

        return jsonify({
            "screener_data": screener_data,
            "insight": reply["candidates"][0]["content"]["parts"][0]["text"]
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# For Render (bind to dynamic port)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
