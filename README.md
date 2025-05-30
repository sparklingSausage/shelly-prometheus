### Shelly-prometheus-exporter
This repository is not actively maintained

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
      - SHELLY_HOSTS=192.168.xx.xx,192.168.xx.xx
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

#### Grafana
Inside Grafana (or Prometheus) you can query the metrics using for example:
```
shelly_power_watts{host="192.168.xx.xx"}
```
