from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route("/")
def home():
    return "Trademark Backend Running"

@app.route("/search")
def search():

    brand = request.args.get("brand")

    if not brand:
        return jsonify({
            "success": False,
            "message": "Brand required"
        })

    try:

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-setuid-sandbox"
                ]
            )

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

            page = context.new_page()

            page.goto(
                "https://www.quickcompany.in/",
                timeout=120000
            )

            page.wait_for_timeout(5000)

            page.goto(
                f"https://www.quickcompany.in/trademarks/search?q={brand}",
                timeout=120000
            )

            page.wait_for_timeout(10000)

            text = page.locator("body").inner_text()

            browser.close()

        lines = text.split("\n")

        results = []

        for line in lines:

            clean = line.strip()

            if brand.lower() in clean.lower():

                if len(clean) > 5:
                    results.append(clean)

        results = list(dict.fromkeys(results))

        return jsonify({
            "success": True,
            "results": results[:25],
            "preview": text[:2000]
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)