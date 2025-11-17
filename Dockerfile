FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    libgl1 libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install CPU-only PyTorch first to avoid heavy CUDA builds
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch torchvision
# Install remaining deps
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/app/
COPY models/ /app/models/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
