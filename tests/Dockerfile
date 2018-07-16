FROM registry.fedoraproject.org/fedora
COPY . /src/
WORKDIR /src
RUN tests/build.sh
RUN tests/config.sh
ENTRYPOINT [ "/usr/sbin/httpd", "-DFOREGROUND" ]
