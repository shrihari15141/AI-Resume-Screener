Deployment helper notes

1) Add gunicorn to requirements.txt
   - Edit requirements.txt and add a new line: gunicorn
   - Example: pip install gunicorn && pip freeze > requirements.txt

2) Ensure CORS is enabled in your Flask app (if frontend runs on a different domain):
   - pip install Flask-Cors
   - In your Flask app (e.g., app.py):
       from flask_cors import CORS
       CORS(app)

3) wsgi.py (already added)
   - Gunicorn will import `app` from wsgi.py. If your Flask app object is defined with a different name or in a different module, edit wsgi.py to import it correctly.

4) Procfile (already added)
   - Render and Heroku-style services use the Procfile start command. It runs gunicorn wsgi:app.

5) Pushing repo to GitHub (local commands):
   git init
   git add .
   git commit -m "Prepare app for deployment"
   # Create a repository on GitHub (via web UI) and then:
   git remote add origin https://github.com/<your-username>/<repo>.git
   git branch -M main
   git push -u origin main

6) Recommended deployment (simplest):
   - Backend: Render (connect GitHub repo, create new Web Service)
     * Build Command: pip install -r requirements.txt
     * Start Command: gunicorn wsgi:app
     * Add environment variables in the Render dashboard (DATABASE_URL, SECRET_KEY, etc.)
   - Frontend: Vercel or Netlify (connect GitHub repo and set build command)
     * Set an environment variable API_URL (point to the Render service URL)

7) Single URL option (optional):
   - Build frontend (npm run build) and copy output into Flask's static/ folder (or serve the build folder).
   - Serve index.html via Flask routes and deploy only the Flask service on Render.

If you want, I can now:
 - Add gunicorn to requirements.txt automatically (I can edit the file), or
 - Prepare a small script to copy the frontend build into Flask static and a Procfile for single-service deploy.

Which of those would you like next?