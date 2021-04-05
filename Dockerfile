FROM python:3.8

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

EXPOSE 80

COPY . /app

CMD streamlit run --server.port 80 --server.enableCORS false streamlit/main.py