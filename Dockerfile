FROM python:3.12
LABEL authors="Ice Wolfy"

WORKDIR /DiscordUtilUserApp/bot

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./bot/main.py" ]
