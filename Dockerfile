FROM python:3.12-slim

WORKDIR /app

# Оптимизация под Docker: отключаем кэш байт-кода (__pycache__) и включаем прямой вывод логов Streamlit в консоль без задержек буфера
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Порт сервера Streamlit по умолчанию
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]