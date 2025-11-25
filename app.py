from flask import Flask, request, send_file, jsonify
import io
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# Hardcoded URL
TARGET_URL = "https://www.toptal.com/developers/keycode"

# Global browser session
browser = None
page = None


def init_browser():
    """Initialize persistent browser session"""
    global browser, page
    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless=True)
    page = browser.new_page()
    page.goto(TARGET_URL, wait_until="networkidle")
    print(f"✓ Browser started and navigated to {TARGET_URL}")


# Initialize on startup
init_browser()


@app.route("/screenshot", methods=["GET"])
def screenshot():
    """Take screenshot of current page"""
    try:
        screenshot_bytes = page.screenshot(type="png")
        return send_file(
            io.BytesIO(screenshot_bytes), mimetype="image/png", as_attachment=False
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/keyboard", methods=["GET"])
def keyboard():
    """
    Press keys via query params
    ?key=Enter  OR  ?text=hello+world
    """
    key = request.args.get("key")
    text = request.args.get("text")

    try:
        if key:
            page.keyboard.press(key)
            return jsonify({"success": True, "action": "press", "key": key})
        elif text:
            page.keyboard.type(text)
            return jsonify({"success": True, "action": "type", "text": text})
        else:
            return jsonify({"error": 'Provide either "key" or "text" query param'}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8327, debug=False, threaded=False)
