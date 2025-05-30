### Shelly-prometheus-exporter
This exporter was quickly made, may include some errors

### What you'll need
- Basic understanding of Docker, Python, Prometheus
- Shelly plug s gen3
- Docker or Python
- Prometheus
- (Grafana) for displaying the metrics


### Structure
- Installation using [Docker](#Docker)
- Installation using [Python](#Python)
- [Prometheus config](#Prometheus)


#### Docker
Run it using the [Docker Compose](docker-compose.yml)
```
services:
  shelly-exporter:
    ports:
      - 8000:8000
    container_name: shelly-exporter
    environment:
      - SHELLY_HOST=http://192.168.x.x
      - POLL_INTERVAL=5
      - PORT=8000
    image: latenightweeb/shelly-prometheus:latest
```

#### Python
Download the [python exporter](exporter.py) file and install all [requirements](requirements.txt) using pip.
Run the it using python

```
python exporter.py
```

#### Prometheus
Add this to your prometheus.yml
```
- job_name: 'shelly_plug'
  scrape_interval: 5s
  static_configs:
    - targets: ['192.168.x.x:8000']
```
