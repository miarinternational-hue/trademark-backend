from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route("/search", methods=["GET"])
def search():

    brand = request.args.get("brand")

    if not brand:
        return jsonify({
            "success": False,
            "message": "Brand required"
        })

    try:

        results = []

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-setuid-sandbox"
                ]
            )

            page = browser.new_page()

            page.goto(
                f"https://www.quickcompany.in/trademarks/search?q={brand}",
                wait_until="networkidle",
                timeout=120000
            )

            page.wait_for_timeout(5000)

            text = page.locator("body").inner_text()

            for line in text.split("\n"):

                clean = line.strip()

                if brand.lower() in clean.lower():

                    if len(clean) > 8:

                        results.append(clean)

            browser.close()

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
    app.run(host="0.0.0.0", port=5000)