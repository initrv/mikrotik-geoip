# MikroTik GeoIP Service

A lightweight FastAPI application that generates MikroTik RouterOS (`.rsc`) scripts for creating country-based firewall address lists. It fetches up-to-date IPv4 aggregated lists from [ipverse/rir-ip](https://github.com/ipverse/rir-ip) and formats them for direct import into MikroTik routers.

## Features

- **Dynamic Generation**: Instantly generates a RouterOS script for any valid country code (ISO 3166-1 alpha-2).
- **Automatic Formatting**: Handles the syntax for `/ip firewall address-list`, including removing old lists before adding new ones.
- **Error Handling**: Gracefully handles invalid country codes and upstream connection issues.
- **Dockerized**: Ready to deploy with Docker and Docker Compose.

## Tech Stack

- **Python 3.12**
- **FastAPI**: High-performance web framework.
- **HTTPX**: Asynchronous HTTP client for fetching upstream data.
- **Uvicorn**: ASGI server.

## Installation & Setup

### Option 1: Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd geoip
    ```

2.  **Start the service:**
    ```bash
    docker compose up --build -d
    ```

The service will be available at `http://localhost:8000`.

### Option 2: Local Installation

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the application:**
    ```bash
    python main.py
    ```
    *Or explicitly with uvicorn:*
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

## Usage

### API Endpoints

#### 1. Health Check
Check if the service is running.
- **URL**: `/`
- **Method**: `GET`
- **Response**: `{"status": "running", "usage": "/geoip/{country_code}"}`

#### 2. Get GeoIP Script
Download the RouterOS script for a specific country.
- **URL**: `/geoip/{country_code}`
- **Method**: `GET`
- **Example**: `/geoip/ru`, `/geoip/us`, `/geoip/cn`
- **Response**: A text stream (file download) containing the RouterOS commands.

### Example: Fetching a List for Russia

You can test it via `curl`:
```bash
curl -O -J http://localhost:8000/geoip/ru
```
This will save a file named `MikroTik-GeoIP-RU.rsc`.

## MikroTik Integration

You can use the service directly from your MikroTik router using the `/tool fetch` command to download and import the list automatically.

**Example RouterOS Script:**

```routeros
/tool fetch url="http://<YOUR_SERVER_IP>:8000/geoip/ru" mode=http dst-path="geoip-ru.rsc"
/import geoip-ru.rsc
```

*Replace `<YOUR_SERVER_IP>` with the IP address of the machine running this service.*
