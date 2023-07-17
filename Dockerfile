FROM archlinux:latest


RUN pacman -Syy --noconfirm && \
    pacman -S --noconfirm git base-devel python python-pip python-setuptools python-wheel

RUN git clone https://github.com/Gentopia-AI/Gentopia.git /opt/Gentopia

RUN cd /opt/Gentopia && \
    python setup.py install

WORKDIR /opt/Gentopia
