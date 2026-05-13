from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import time

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

        results = []

        with sync_playwright() as p:

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )

            context = browser.new_context()

            page = context.new_page()

            page.goto(
                "https://www.quickcompany.in/trademarks",
                timeout=90000,
                wait_until="domcontentloaded"
            )

            time.sleep(5)

            inputs = page.locator("input:visible")

            count = inputs.count()

            if count > 0:

                search_box = inputs.nth(0)

                search_box.click()

                time.sleep(1)

                search_box.fill(brand)

                time.sleep(1)

                page.keyboard.press("Enter")

                time.sleep(8)

                body_text = page.locator("body").inner_text()

                for line in body_text.split("\n"):

                    clean = line.strip()

                    if brand.lower() in clean.lower():

                        if len(clean) > 10:

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

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )