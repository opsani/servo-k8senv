# Only works in cluster
FROM python:3.6-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /servo

# Install required packages
ADD  https://storage.googleapis.com/kubernetes-release/release/v1.16.2/bin/linux/amd64/kubectl /usr/local/bin/

ADD ./requirements.txt /servo/
RUN pip3 install -r requirements.txt

ADD https://raw.githubusercontent.com/opsani/servo/preflight-env-mode/servo \
    https://raw.githubusercontent.com/opsani/servo/master/adjust.py \
    https://raw.githubusercontent.com/opsani/servo/master/measure.py \
    https://raw.githubusercontent.com/opsani/servo-prom/master/measure \
    https://raw.githubusercontent.com/opsani/servo-k8s/master/adjust \
    /servo/

# Add seperately from downloads for faster build
ADD ./environment /servo/ 

RUN chmod a+rx /servo/adjust /servo/measure /servo/environment /servo/servo /usr/local/bin/kubectl && \
 	chmod a+r /servo/adjust.py /servo/measure.py

ENTRYPOINT [ "python3", "servo" ]
