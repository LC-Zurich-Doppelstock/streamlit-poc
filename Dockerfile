FROM python:3.10-slim AS build
WORKDIR /app
ENV TZ=UTC
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src src

FROM build AS streamlit
EXPOSE 8501
ENTRYPOINT [ "streamlit", "run", "src/webling/app.py", "--server.port=8501", "--server.address=0.0.0.0" ]