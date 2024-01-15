FROM python:3.10-slim AS build
WORKDIR /app
ENV TZ=UTC
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src src

FROM build AS streamlit
ARG PORT=8501
EXPOSE $PORT
ENV PORT=$PORT
CMD streamlit run src/webling/app.py --server.port=$PORT --server.address=0.0.0.0