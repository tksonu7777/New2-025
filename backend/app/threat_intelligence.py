import requests
import logging
import base64
from .config import settings

logger = logging.getLogger(__name__)

def check_ip_abuseipdb(ip_address: str):
    """
    Checks an IP address against the AbuseIPDB API.
    """
    url = f"https://api.abuseipdb.com/api/v2/check"
    headers = {
        "Accept": "application/json",
        "Key": settings.abuseipdb_api_key,
    }
    params = {
        "ipAddress": ip_address,
        "maxAgeInDays": settings.max_age_in_days,
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get("data", {})
        return {
            "abuse_confidence_score": data.get("abuseConfidenceScore", 0),
            "is_whitelisted": data.get("isWhitelisted"),
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling AbuseIPDB API: {e}")
        return None

def check_url_virustotal(url: str):
    """
    Checks a URL against the VirusTotal API.
    """
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
    api_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    headers = {
        "accept": "application/json",
        "x-apikey": settings.virustotal_api_key,
    }
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json().get("data", {}).get("attributes", {})
        stats = data.get("last_analysis_stats", {})
        return {
            "harmless": stats.get("harmless", 0),
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling VirusTotal API: {e}")
        return None
