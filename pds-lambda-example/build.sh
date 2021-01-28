#!/bin/bash
set -ex

# This build script creates a zip file, venv.zip, containing a Lambda function
# and a Python virtual environment with ObsPy installed.

# Yum installations have been moved to Dockerfile.
#yum update -y
#yum install -y \
#    atlas-devel \
#    atlas-sse3-devel \
#    blas-devel \
#    freetype-devel \
#    libpng-devel \
#    gcc \
#    gcc-c++ \
#    gcc72-c++ \
#    gcc-gfortran \
#    lapack-devel \
#    libjpeg-turbo \
#    libjpeg-turbo-devel \
#    findutils \
#    zip \
#    tar

PYTHON=python3.7

do_pip () {
  pip install --upgrade pip wheel
  pip install --no-binary :all: numpy==1.19.5
  pip install --no-binary :all: scipy==1.6.0
  pip install --no-binary :all: obspy==1.2.2
  #test -f /outputs/requirements.txt && pip install -r /outputs/requirements.txt
}

strip_virtualenv () {
    # Without dist-info, obspy.read() complains that a miniSEED file
    # is in an unknown format, so don't delete dist-info. The resulting zip
    # file is actually smaller. 
    #find $VIRTUAL_ENV -name "*.dist-info" -type d -prune -exec rm -rf {} \;
    #echo "venv stripped size $(du -sh $VIRTUAL_ENV | cut -f1)"

    # ObsPy does not need to be moved before removing "tests".
    #tar -cvf "$VIRTUAL_ENV/lib64/python3.7/site-packages/obspy.tar" "$VIRTUAL_ENV/lib64/python3.7/site-packages/obspy"
    #rm -rf "$VIRTUAL_ENV/lib64/python3.7/site-packages/obspy"

    # Clean up tests
    find $VIRTUAL_ENV -name "tests" -type d -prune -exec rm -rf {} \;
    echo "venv stripped size $(du -sh $VIRTUAL_ENV | cut -f1)"

    #tar -xvf "$VIRTUAL_ENV/lib64/python3.7/site-packages/obspy.tar"
    #rm -rf "$VIRTUAL_ENV/lib64/python3.7/site-packages/obspy.tar"
    
    echo "venv original size $(du -sh $VIRTUAL_ENV | cut -f1)"
    find $VIRTUAL_ENV/lib64/python3.7/site-packages/ -name "*.so" | xargs strip
    echo "venv stripped size $(du -sh $VIRTUAL_ENV | cut -f1)"

    cp /outputs/process.py $VIRTUAL_ENV

    pushd $VIRTUAL_ENV && zip -r -9 -q /tmp/process.zip process.py ; popd
    pushd $VIRTUAL_ENV/lib/python3.7/site-packages/ && zip -r -9 --out /tmp/partial-venv.zip -q /tmp/process.zip * ; popd
    pushd $VIRTUAL_ENV/lib64/python3.7/site-packages/ && zip -r -9 --out /outputs/venv.zip -q /tmp/partial-venv.zip * ; popd
    echo "site-packages compressed size $(du -sh /outputs/venv.zip | cut -f1)"

    pushd $VIRTUAL_ENV && zip -r -q /outputs/full-venv.zip * ; popd
    echo "venv compressed size $(du -sh /outputs/full-venv.zip | cut -f1)"
}

shared_libs () {
    libdir="$VIRTUAL_ENV/lib64/python3.7/site-packages/lib/"
    mkdir -p $VIRTUAL_ENV/lib64/python3.7/site-packages/lib || true
    cp /usr/lib64/atlas/* $libdir
    cp /usr/lib64/libquadmath.so.0 $libdir
    cp /usr/lib64/libgfortran.so.3 $libdir
    cp /usr/lib64/libfreetype.so.6 $libdir
    cp /usr/lib64/libpng.so.3 $libdir
    cp /usr/lib64/libblas.so.3 $libdir 
    cp /usr/lib64/liblapack.so.3 $libdir
    #cp /usr/lib64/* $libdir
}

main () {
    #/usr/bin/virtualenv \
    #    --python /usr/bin/python /obspy_build \
    #    --always-copy \
    #    --no-site-packages
    $PYTHON -m venv /obspy_build
    . /obspy_build/bin/activate

    do_pip

    shared_libs

    strip_virtualenv

}
main
