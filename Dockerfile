FROM python

ENV TZ="Asia/Singapore"
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /
RUN mkdir -p staycation/app
COPY app /staycation/app
COPY requirements.txt /staycation

# WORKDIR /staycation/app
WORKDIR /staycation
RUN pip3 install -r requirements.txt --no-cache-dir 
RUN pip3 install gunicorn --no-cache-dir && \
    pip3 install Werkzeug==2.2.2 --no-cache-dir 
    # wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | apt-key add - && \
    # echo 'deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse' | tee -a /etc/apt/sources.list.d/mongodb-org-7.0.list && \
    # apt update && \
    # apt install mongodb-org -y
    
    # The followings works for Ubuntu 20.04 on AWS EC2
    # wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc |  gpg --dearmor | sudo tee /usr/share/keyrings/mongodb.gpg > /dev/null 
    # echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
    # sudo apt update
    # sudo apt install mongodb-org

WORKDIR /staycation
# # ENV PYTHONPATH=/staycation/app
# ENV PYTHONPATH=/staycation

# EXPOSE 5000
# # CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-m", "007", "app:app"]
#CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-m", "007", "app:create_app()"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-m", "007", "--worker-class", "gevent", "--workers", 5, "--worker-connections", 1000, "app:create_app()"]