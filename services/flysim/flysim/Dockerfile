FROM python:3.12.7-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY install_codon_v0.17.0.sh .
RUN yes y | bash install_codon_v0.17.0.sh

COPY . .
