from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/screener', methods=['POST'])  # ✅ MUST have methods=['POST']
def screener():
    try:
        data = request.get_json()
        stock = data.get("stock", "")
        
        # ✅ Validate input
        if not stock:
            return jsonify({"error": "Stock symbol is missing"}), 400

        url = f"https://www.screener.in/company/{stock}/consolidated/"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")
        
        ratios = soup.find_all("li", class_="flex flex-space-between")
        company_url = f"https://www.screener.in/company/{stock}/"

        response = {
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

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "✅ Screener Scraper Running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
