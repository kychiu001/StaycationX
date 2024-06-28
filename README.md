# [Staycation API branch]

- Added controllers/api.py and models/token.py
- requirements.txt `flask-httpauth` and `Flask-CORS` (which is to allow cross original calls form ReactJS)

## Containerization

- Added Dockerfile to run the flask app under Gunicorn as a container


# [Saycation Nginx branch]

- To run web, app and db server processes manually
  
* `gunicorn --bind 0.0.0.0:5000 -m 007 -e FLASK_ENV=development --workers=5 "app:create_app()"` 
* or `FLASK_ENV="development" gunicorn --bind 0.0.0.0:5000 -m 007 --workers=5 "app:create_app()"`
* `sudo nginx -c /d/Desktop/ICT381/tars/staycationX/nginx.conf`
