FROM python:3.12

ENV TZ="Asia/Singapore"
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt install sudo wget gnupg curl -y && \
    install -d -m 0755 /etc/apt/keyrings && \
    wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null && \
    echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null && \
    printf "Package: *\nPin: origin packages.mozilla.org\nPin-Priority: 1000\n" > /etc/apt/preferences.d/mozilla && \
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor && \
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list && \
    apt-get update && \
    apt install firefox mongodb-org -y && \
    rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /staycation

# Copy application files
COPY app /staycation/app
COPY tests /staycation/app/tests
COPY requirements.txt /staycation/
COPY .env /staycation/.env
COPY db_seed /staycation//db_seed
COPY geckodriver /staycation/geckodriver

# Install Python dependencies
RUN pip3 install -r requirements.txt --no-cache-dir && \
    pip3 install gunicorn Werkzeug==2.2.2 --no-cache-dir


# Prepare MongoDB configuration
RUN sed -i 's/bindIp: 127.0.0.1/bindIp: 0.0.0.0/' /etc/mongod.conf && \
    mkdir -p data/db

# Set up geckodriver
RUN chmod a+x /staycation/geckodriver

# Expose the application port
EXPOSE 5000
EXPOSE 27017

# Startup script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

