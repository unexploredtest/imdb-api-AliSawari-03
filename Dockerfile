FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip

WORKDIR /app
COPY . .

RUN pip3 install -r requirements.txt --break-system-packages
RUN python3 process_data.py

CMD ["python3", "api.py"]