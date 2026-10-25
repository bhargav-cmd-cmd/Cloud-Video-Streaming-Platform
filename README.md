# VidiStream — Video Streaming Platform

VidiStream is a full-stack video sharing and streaming application built with Flask, SQLite, HTML, CSS, and JavaScript. Users can register, upload videos, watch content, and manage their uploads through a creator dashboard.

Videos and thumbnails are stored on the machine running Flask. User and video records are saved in a local SQLite database, and Flask serves uploaded media directly.

## Features

- User registration and login with password hashing
- Video uploads with a 100 MB request limit
- Upload formats: MP4, WebM, OGG, MOV, and MKV (playback depends on browser codec support)
- Video playback and seeking through HTTP range requests
- Custom thumbnails and automatic thumbnail extraction using OpenCV
- Search by title or description
- Creator dashboard with video counts, total views, and average views
- Editing video details and deleting your own uploads
- View counter and recommendations showing other recent uploads
- Responsive Bootstrap interface

## Technology

- **Backend:** Python, Flask, Flask-Login, Flask-SQLAlchemy, Werkzeug
- **Database:** SQLite
- **Media processing:** OpenCV
- **Frontend:** HTML, CSS, JavaScript, Bootstrap, Font Awesome

## Project structure

```text
VidiStream/
├── app.py                 # Application setup and configuration
├── models.py              # User and video models
├── requirements.txt       # Python dependencies
├── routes/
│   ├── auth.py            # Registration, login, and logout
│   ├── main.py            # Home, search, and dashboard
│   └── video.py           # Uploads, playback, thumbnails, edits, and deletion
├── templates/             # Jinja HTML templates
├── static/
│   ├── css/style.css
│   └── js/main.js
├── uploads/
│   ├── videos/            # Uploaded video files
│   └── thumbnails/        # Uploaded or generated thumbnails
├── instance/
│   └── database.db        # SQLite database, created automatically
└── README.md
```

The top-level folder name can differ depending on where you cloned or extracted the project.

## Run locally

Open a terminal in the project directory and create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux, activate it with `source .venv/bin/activate` instead.

Install dependencies and start the application:

```text
python -m pip install -r requirements.txt
python app.py
```

Visit **http://127.0.0.1:5000**. The application creates database tables and upload directories automatically. Register an account to upload and manage videos.

## Storage and deployment

- Uploaded media is stored under `uploads/`.
- Accounts and video metadata are stored in `instance/database.db`.
- Back up both the database and uploaded media to preserve application data.
- Bootstrap and Font Awesome load from external CDNs, so those interface assets require internet access.
- The included launch command uses Flask's development server with debug mode enabled. Before public deployment, configure a private secret key, disable debug mode, and use a production WSGI server.
