from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.json.sort_keys = False


# ---------- Helper Functions ----------


def get_headers():
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'downlink': '10',
        'dpr': '1.25',
        'ect': '4g',
        'priority': 'u=0, i',
        'rtt': '50',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
        'viewport-width': '883',
    }


def fetch_page(query):
    url = f"https://www.amazon.in/s?k={query}"
    headers = get_headers()
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')


def parse_product(item):
    try:
        title = item.find('div', attrs={'data-cy': 'title-recipe'}).text.strip()
        show_price = item.find('span', attrs={'class': 'a-price-whole'}).text.strip().replace(',', '')
        actual_price = item.find('div', attrs={'class': 'aok-inline-block'}).find_all('span')[-1].text.replace(',', '')[1:]
        discount = item.find('div', attrs={'class': 'a-color-base'}).find_all('span')[-1].text.split("%")[0].replace("(", "")
        rating = item.find('span', attrs={'class': 'a-icon-alt'}).text.split(" ")[0].strip() if item.find('span', attrs={'class': 'a-icon-alt'}) else 'undetermined'
        ratedby = item.find('span', attrs={'class': 'a-size-base s-underline-text'}).text.replace(',', '') if item.find('span', attrs={'class': 'a-size-base s-underline-text'}) else 'undetermined'
        link = "https://www.amazon.in" + item.find('a', attrs={'class': 'a-link-normal'})['href'].split('/ref=')[0]

        if link.startswith('https://www.amazon.in/sspa/click?') :
            return {"error": "Sponsored Product"}

        return {
            "title": title,
            "link": link,
            "show_price": show_price,
            "actual_price": actual_price,
            "discount": discount,
            "rating": rating,
            "ratedby": ratedby
        }
    except Exception as e:
        return {"error": "Parsing failed", "details": str(e)}


def scrape_amazon(query):
    soup = fetch_page(query)
    results = []
    for item in soup.find_all('div', attrs={'role': 'listitem', 'data-component-type': 's-search-result'}):
        product = parse_product(item)
        if "error" not in product:
            results.append(product)
    return results


# ---------- Routes ----------


@app.route('/scrape', methods=['GET'])
def scrape_route():
    query = request.args.get('query', default='smartphone')
    try:
        data = scrape_amazon(query)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Scraping failed", "details": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)
