FROM amazonlinux:2018.03
RUN yum update -y
RUN yum groupinstall "Development Tools" -y
RUN yum install -y \
   gcc \
    bzip2-devel \
    libffi \
    openssl-devel \
    perl-core \
    zlib-devel \
    libxml2-devel \
    libxslt-devel \
    libffi-devel \
    libcffi-devel \
    wget \


RUN cd /usr/src/ && \
    wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz && \
    tar xzf Python-3.7.4.tgz && \
    cd Python-3.7.4 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd / && rm -rf /usr/src/Python-3.7.4.tgz

