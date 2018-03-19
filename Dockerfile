FROM python:alpine
RUN pip install flask requests
ENTRYPOINT ["python3", "/main.py"]
RUN mkdir -p /var/log/LogDAG
RUN mkdir -p /var/log/blocks
COPY logdag.py /main.py
