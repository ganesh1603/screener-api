from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/screener', methods=['POST'])
def screener_scraper():
    try:
        data = request.json
        stock_name = data.get("stock")
        if not stock_name:
            return jsonify({"error": "Missing 'stock' in request"}), 400

        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        search_url = f"https://www.screener.in/search/?q={stock_name}"
        search_res = requests.get(search_url, headers=headers)
        search_soup = BeautifulSoup(search_res.text, "html.parser")
        company_link_tag = search_soup.select_one(".search-list a")
        if not company_link_tag:
            return jsonify({"error": "Company not found"})

        company_url = "https://www.screener.in" + company_link_tag['href']
        res = requests.get(company_url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        name = soup.select_one("h1").text.strip()
        ratios = soup.select("li.flex.flex-space-between b")

        data = {
            "Company": name,
            "ROCE": ratios[0].text if len(ratios) > 0 else "",
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

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/', methods=['GET'])
def home():
    return "Screener Scraper API working!", 200