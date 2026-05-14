from flask import Flask, request, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# ENABLE CORS
CORS(app)

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

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

            page = context.new_page()

            # OPEN QUICKCOMPANY

            page.goto(
                "https://www.quickcompany.in/",
                timeout=120000
            )

            page.wait_for_timeout(5000)

            # SEARCH

            search_input = page.locator("input").first

            search_input.click()

            search_input.fill(brand)

            page.keyboard.press("Enter")

            page.wait_for_timeout(10000)

            # GET PAGE TEXT

            body_text = page.locator("body").inner_text()

            browser.close()

        lines = body_text.split("\n")

        for i, line in enumerate(lines):

            clean = line.strip()

            if brand.lower() in clean.lower():

                item = clean

                # ADD NEXT LINES AS DETAILS

                if i + 1 < len(lines):
                    item += " | " + lines[i + 1].strip()

                if i + 2 < len(lines):
                    item += " | " + lines[i + 2].strip()

                if i + 3 < len(lines):
                    item += " | " + lines[i + 3].strip()

                if len(item) > 10:
                    results.append(item)

        # REMOVE DUPLICATES

        results = list(dict.fromkeys(results))

        return jsonify({
            "success": True,
            "results": results[:25]
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)