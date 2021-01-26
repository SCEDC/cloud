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
    atlas-devel \
    atlas-sse3-devel \
    blas-devel \
    freetype-devel \
    libpng-devel \
    gcc-c++ \
    gcc72-c++ \
    gcc-gfortran \
    lapack-devel \
    libjpeg-turbo \
    libjpeg-turbo-devel \
    findutils \
    zip \
    tar



RUN cd /usr/src/ && \
    wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz && \
    tar xzf Python-3.7.4.tgz && \
    cd Python-3.7.4 && \
    ./configure --enable-optimizations && \
    make altinstall && \
    cd / && rm -rf /usr/src/Python-3.7.4.tgz

