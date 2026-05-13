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

            page = browser.new_page()

            page.goto(
                f"https://www.quickcompany.in/trademarks/search?q={brand}",
                wait_until="domcontentloaded",
                timeout=120000
            )

            page.wait_for_timeout(8000)

            html = page.content()

            browser.close()

        import re

        matches = re.findall(
            rf".{{0,40}}{brand}.{{0,80}}",
            html,
            re.IGNORECASE
        )

        clean_results = []

        for m in matches:

            text = re.sub("<.*?>", "", m)
            text = text.strip()

            if len(text) > 5:
                clean_results.append(text)

        clean_results = list(dict.fromkeys(clean_results))

        return jsonify({
            "success": True,
            "results": clean_results[:20]
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })