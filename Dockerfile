FROM python:3.7.3
LABEL maintainer="Łukasz Podeszwa"

# Use env vars during runtime
ENV localhost_ip="0.0.0.0"
ENV port=""
ENV db_uri=""

# Set workdir
WORKDIR /workdir

# Copy requrirements
COPY requirements.txt ./

# Install 
RUN apt-get update
RUN apt-get remove gunicorn -y
RUN apt install python3-pip -y

# Update pip and install requirements
RUN pip uninstall gunicorn
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 uninstall gunicorn -y
RUN pip3 install git+https://github.com/benoitc/gunicorn.git
RUN mkdir /workdir/images

# Copy all files to workdir
COPY . .

# Run flask server on runtime
CMD export PYTHONPATH=/workdir && gunicorn -b ${localhost_ip}:${port} \
    -e DATABASE_URI=${db_uri} \
    -e MAILJET_ID=${mailjet_id} \
    -e MAILJET_SECRET=${mailjet_secret} \
    -e MJML_ID=${mjml_id} \
    -e MJML_SECRET=${mjml_secret} \
    -e OAUTH_GOOGLE_CLIENT_ID=${oauth_google_client_id} \
    -e OAUTH_GOOGLE_CLIENT_SECRET=${oauth_google_client_secret} \
    -e OAUTH_GOOGLE_REDIRECT_URI=${oauth_google_redirect_uri} \
    -e API_IMAGES_DIR=${api_images_uri} \
    'api.app:init_app()'