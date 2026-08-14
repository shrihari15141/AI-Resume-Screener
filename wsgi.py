# wsgi.py — entrypoint for WSGI servers (gunicorn)
# Update the import below if your Flask app object is defined elsewhere.
try:
    from app import app  # common: app.py defines `app`
except Exception:
    try:
        from main import app  # common alternative: main.py
    except Exception:
        try:
            from resumescreener import app  # package-style import
        except Exception:
            raise RuntimeError("Could not import Flask 'app'. Edit wsgi.py to import your Flask app object.")

# When run directly, start the Flask dev server (not used in production on Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
