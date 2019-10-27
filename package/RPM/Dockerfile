FROM centos:7
RUN yum install -y python3 python-psutil python-twisted wmctrl gnupg fakeroot rpm-build
RUN mkdir pyacry2
COPY . pyacryl2
RUN cd pyacryl2 && python3 setup.py bdist_rpm