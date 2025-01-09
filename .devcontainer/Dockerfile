FROM debian:buster-slim

# Install main packages and Python 2.7
RUN apt-get update && apt-get install -y \
    python2.7 \
    python2.7-dev \
    python-pip \
    gwyddion \
    python-gtk2 \
    xvfb

# Ensure python2.7 is used as the default
RUN ln -sf /usr/bin/python2.7 /usr/bin/python

# Install Python 2.7 versions of the required libraries
RUN pip install --no-cache-dir \
    numpy==1.16.2 \
    scipy==1.2.3 \
    pandas==0.24.2 
    
# Required for gwyutils
ENV PYTHONPATH "${PYTHONPATH}:/usr/share/gwyddion/pygwy"