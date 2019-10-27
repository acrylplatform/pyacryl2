FROM ubuntu:18.04
RUN apt update
RUN apt-get install -y python3-all python3-setuptools python3-pip ruby ruby-dev rubygems build-essential
RUN gem install --no-ri --no-rdoc fpm
RUN mkdir pyacryl2
RUN mkdir result
COPY . pyacryl2
WORKDIR pyacryl2
CMD bash build_deb.sh