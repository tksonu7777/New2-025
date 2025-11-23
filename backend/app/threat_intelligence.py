import requests
import logging
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
