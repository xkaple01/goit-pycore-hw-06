FROM python:3.11

WORKDIR /goit-pycore-hw-06
COPY . .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["gunicorn", "app:me", "--bind", "0.0.0.0:8080"]