FROM python:3.9 AS builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.9-slim
WORKDIR /bot_code/

COPY --from=builder /root/.local /root/.local
COPY contact_book_bot/src/ .

ENV PATH=/root/.local:$PATH
CMD ["python", "-u", "main_bot.py"]