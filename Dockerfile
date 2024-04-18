FROM python:3-alpine
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 2000
CMD python -u /app/bot.py
