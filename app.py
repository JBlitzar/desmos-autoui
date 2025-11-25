from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import time
import threading
from playwright.sync_api import sync_playwright
from queue import Queue

app = Flask(__name__)
CORS(app)

TARGET_URL = "https://thelast.io"
WINDOW_WIDTH = 1728
WINDOW_HEIGHT = 894

browser = None
page = None
playwright_instance = None
context = None
key_states = {"w": False, "a": False, "s": False, "d": False}
screenshot_queue = Queue(maxsize=1)
command_queue = Queue()
latest_screenshot = None
screenshot_lock = threading.Lock()


def playwright_worker():
    """Worker thread that handles all Playwright operations"""
    global browser, page, playwright_instance, context, latest_screenshot

    playwright_instance = sync_playwright().start()
    browser = playwright_instance.firefox.launch(headless=True)
    context = browser.new_context(
        viewport={"width": WINDOW_WIDTH, "height": WINDOW_HEIGHT}
    )
    page = context.new_page()
    page.goto(TARGET_URL, wait_until="networkidle")
    print(f"✓ Browser started at {TARGET_URL} with size {WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    time.sleep(10)
    print("✓ Waited 10 seconds for page load")

    page.mouse.click(913, 788)
    print("✓ Clicked at (864, 162)")
    time.sleep(0.5)

    page.mouse.click(864, 162)
    print("✓ Clicked at (864, 162)")

    time.sleep(0.5)

    page.keyboard.type("test")
    print("✓ Typed 'test'")

    time.sleep(0.5)

    page.mouse.click(864, 258)
    print("✓ Clicked at (864, 258)")
    print("✓ Startup sequence complete")

    while True:
        if not command_queue.empty():
            cmd = command_queue.get()
            try:
                if cmd["action"] == "screenshot":
                    jpeg_bytes = page.screenshot(type="jpeg", quality=80)
                    with screenshot_lock:
                        latest_screenshot = jpeg_bytes
                elif cmd["action"] == "toggle_key":
                    key = cmd["key"]
                    key_states[key] = not key_states[key]
                    if key_states[key]:
                        page.keyboard.down(key)
                    else:
                        page.keyboard.up(key)
                elif cmd["action"] == "press_key":
                    page.keyboard.press(cmd["key"])
                elif cmd["action"] == "click":
                    page.mouse.click(cmd["x"], cmd["y"])
            except Exception as e:
                print(f"Command error: {e}")
        else:
            try:
                jpeg_bytes = page.screenshot(type="jpeg", quality=80)
                with screenshot_lock:
                    latest_screenshot = jpeg_bytes
            except Exception as e:
                print(f"Screenshot error: {e}")
            time.sleep(0.033)


playwright_thread = threading.Thread(target=playwright_worker, daemon=True)
playwright_thread.start()
time.sleep(1)


def get_screenshot_jpeg():
    """Get current screenshot as JPEG bytes"""
    with screenshot_lock:
        return latest_screenshot if latest_screenshot else b""


def generate_mjpeg_stream():
    """Generate MJPEG stream"""
    while True:
        try:
            jpeg_bytes = get_screenshot_jpeg()
            if jpeg_bytes:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + jpeg_bytes + b"\r\n"
                )
            time.sleep(0.033)
        except Exception as e:
            print(f"Stream error: {e}")
            break


@app.route("/stream", methods=["GET"])
def stream():
    """MJPEG livestream endpoint"""
    return Response(
        generate_mjpeg_stream(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/tw", methods=["GET", "POST"])
def toggle_w():
    """Toggle W key"""
    try:
        command_queue.put({"action": "toggle_key", "key": "w"})
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ta", methods=["GET", "POST"])
def toggle_a():
    """Toggle A key"""
    try:
        command_queue.put({"action": "toggle_key", "key": "a"})
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ts", methods=["GET", "POST"])
def toggle_s():
    """Toggle S key"""
    try:
        command_queue.put({"action": "toggle_key", "key": "s"})
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/td", methods=["GET", "POST"])
def toggle_d():
    """Toggle D key"""
    try:
        command_queue.put({"action": "toggle_key", "key": "d"})
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/pspace", methods=["GET", "POST"])
def press_space():
    """Press space key"""
    try:
        command_queue.put({"action": "press_key", "key": " "})
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/p1", methods=["GET", "POST"])
def press_1():
    """Press 1 key"""
    try:
        command_queue.put({"action": "press_key", "key": "1"})
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/p2", methods=["GET", "POST"])
def press_2():
    """Press 2 key"""
    try:
        command_queue.put({"action": "press_key", "key": "2"})
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/p3", methods=["GET", "POST"])
def press_3():
    """Press 3 key"""
    try:
        command_queue.put({"action": "press_key", "key": "3"})
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/p4", methods=["GET", "POST"])
def press_4():
    """Press 4 key"""
    try:
        command_queue.put({"action": "press_key", "key": "4"})
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/p5", methods=["GET", "POST"])
def press_5():
    """Press 5 key"""
    try:
        command_queue.put({"action": "press_key", "key": "5"})
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/p6", methods=["GET", "POST"])
def press_6():
    """Press 6 key"""
    try:
        command_queue.put({"action": "press_key", "key": "6"})
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/pe", methods=["GET", "POST"])
def press_e():
    """Press E key"""
    try:
        command_queue.put({"action": "press_key", "key": "e"})
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/click", methods=["GET", "POST"])
def click():
    """Click at current mouse position or specified coordinates"""
    try:
        x = request.args.get("x", type=int)
        y = request.args.get("y", type=int)
        if x is not None and y is not None:
            command_queue.put({"action": "click", "x": x, "y": y})
        else:
            command_queue.put(
                {"action": "click", "x": WINDOW_WIDTH // 2, "y": WINDOW_HEIGHT // 2}
            )
        return Response(
            generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8327, debug=False, threaded=True)
