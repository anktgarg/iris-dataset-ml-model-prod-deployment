FROM ubuntu:latest
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
&& apt install -y apache2 apache2-dev vim \
&& apt install -y python3-pip libapache2-mod-wsgi-py3 \
&& apt install -y python3-sklearn \
&& apt-get clean \
&& apt-get autoremove \
&& rm -rf /var/lib/apt/lists/* \
&& mkdir -p /var/www/html/web
COPY ./000-default.conf /etc/apache2/sites-available/000-default.conf
COPY ./app.wsgi /var/www/html/web
COPY ./init.py /var/www/html/web
COPY ./iris_trained_model.pkl /var/www/html/web
COPY ./requirements.txt /var/www/html/web
WORKDIR /var/www/html/web
RUN pip3 install -r requirements.txt
EXPOSE 80
ENTRYPOINT ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
