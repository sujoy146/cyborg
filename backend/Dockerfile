FROM python:3.11-slim

WORKDIR /app

# Install CPU-only PyTorch first (saves ~1.5GB vs CUDA)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create writable data directory for table.json
RUN mkdir -p /data && cp table.json /data/table.json 2>/dev/null || echo '{"version":2,"next_id":1,"entries":{}}' > /data/table.json

# HuggingFace Spaces expects port 7860
EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
