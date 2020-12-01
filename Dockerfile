FROM python:3-alpine

RUN apk update
RUN apk add bash nano chromium chromium-chromedriver

# RUN rm  -rf /tmp/* /var/cache/apk/* &&\
#     wget "https://github.com/mozilla/geckodriver/releases/download/v0.28.0/geckodriver-v0.28.0-linux64.tar.gz" &&\
#     tar -xvf geckodriver-v0.28.0-linux64.tar.gz &&\
#     rm -rf geckodriver-v0.28.0-linux64.tar.gz &&\
#     chmod a+x geckodriver && chmod 777 geckodriver &&\
#     mv geckodriver /usr/bin/

COPY ./requirements.txt /var/www/requirements.txt
RUN pip3 install -r /var/www/requirements.txt
RUN pip3 install pytest
