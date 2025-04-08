from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.json.sort_keys = False


def getSoup(response):
    return BeautifulSoup(response.text, 'html.parser')


@app.route('/scrape', methods=['GET'])
def scrape_amazon():
    query = request.args.get('query', default="smartphone", type=str)  # Get query from URL, default is 'cat'

    url = f"https://www.amazon.in/s?k={query}"

    headers = {
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

    try:
        soup = getSoup(requests.get(url, headers=headers))

        result = []

        for i in soup.find_all('div', attrs={'role': 'listitem', 'data-component-type': 's-search-result'}):
            title = i.find('div', attrs={'data-cy': 'title-recipe'}).text.strip().replace("SponsoredSponsored You are seeing this ad based on the product’s relevance to your search query.Let us know","")
            show_price = i.find('span', attrs={'class': 'a-price-whole'}).text.strip().replace(',', '')
            actual_price = i.find('div', attrs={'class': 'aok-inline-block'}).find_all('span')[-1].text.replace(',', '')[1:]
            discount = i.find('div', attrs={'class': 'a-color-base'}).find_all('span')[-1].text.split("%")[0].replace("(", "")
            rating = i.find('span', attrs={'class': 'a-icon-alt'}).text.split(" ")[0].strip() if i.find('span', attrs={'class': 'a-icon-alt'}) else 'undetermined'
            ratedby = i.find('span', attrs={'class': 'a-size-base s-underline-text'}).text.replace(',', '') if i.find('span', attrs={'class': 'a-size-base s-underline-text'}) else 'undetermined'

            link = "https://www.amazon.in" + i.find('a', attrs={'class': 'a-link-normal'})['href'].split('/ref=')[0]

            result.append({
                "title": title,
                "link": link,
                "show_price": show_price,
                "actual_price": actual_price,
                "discount": discount,
                "rating": rating,
                "ratedby": ratedby
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
