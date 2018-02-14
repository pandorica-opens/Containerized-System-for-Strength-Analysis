from ubuntu:16.04
maintainer OJ
user root

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8


RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion

#RUN add-apt-repository ppa:fenics-packages/fenics

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/archive/Anaconda3-4.4.0-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /opt/conda && \
    rm ~/anaconda.sh

RUN apt-get install -y software-properties-common  build-essential curl grep sed dpkg  &&  \
    add-apt-repository ppa:fenics-packages/fenics && apt-get update && apt-get install -y fenics && \
    TINI_VERSION=`curl https://github.com/krallin/tini/releases/latest | grep -o "/v.*\"" | sed 's:^..\(.*\).$:\1:'` && \
    curl -L "https://github.com/krallin/tini/releases/download/v${TINI_VERSION}/tini_${TINI_VERSION}.deb" > tini.deb && \
    dpkg -i tini.deb && \
    rm tini.deb && \
    apt-get clean

ENV PATH /opt/conda/bin:$PATH

run conda install python=3.5 -y --quiet
run conda install -c conda-forge -c dlr-sc -c pythonocc -c oce pythonocc-core==0.18 python=3.5 -y --quiet
run pip install fenics-ffc --upgrade
run conda install -c conda-forge fenics
run conda install jupyter -y --quiet
run apt-get -y install gmsh
run mkdir /opt/notebooks

run cd /home && \
    git clone https://github.com/root-project/root.git

