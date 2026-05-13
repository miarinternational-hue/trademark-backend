from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/search", methods=["GET"])
def search_trademark():

    brand = request.args.get("brand")

    if not brand:
        return jsonify({
            "success": False,
            "message": "Brand required"
        })

    try:

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        url = f"https://www.quickcompany.in/trademarks/search?q={brand}"

        response = requests.get(
            url,
            headers=headers,
            timeout=30,
            verify=False
        )

        soup = BeautifulSoup(response.text, "html.parser")

        text = soup.get_text("\n")

        results = []

        for line in text.split("\n"):

            clean = line.strip()

            if brand.lower() in clean.lower():

                if len(clean) > 8:

                    results.append(clean)

        results = list(dict.fromkeys(results))

        return jsonify({
            "success": True,
            "results": results[:20]
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )