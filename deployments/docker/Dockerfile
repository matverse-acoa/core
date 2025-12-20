FROM python:3.11-slim as builder
WORKDIR /build
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*
COPY requirements/base.txt .
RUN pip install --no-cache-dir --user -r base.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY src/ ./src/
COPY api/ ./api/
COPY configs/ ./configs/
RUN useradd -m -u 1000 acoa && chown -R acoa:acoa /app
USER acoa
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
