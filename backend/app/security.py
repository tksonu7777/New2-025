from . import schemas, threat_intelligence, crud
from .config import settings
from imagehash import average_hash, hex_to_hash
from sqlalchemy.orm import Session
from typing import List
from PIL import Image
import io
import base64

def analyze_api_call(api_call: schemas.ApiCallCreate):
    """
    Analyzes an API call for suspicious activity.
    """
    # Placeholder for more sophisticated analysis
    if "password" in api_call.payload.lower():
        return {"risk_score": 8, "is_suspicious": True}
    return {"risk_score": 2, "is_suspicious": False}

def analyze_device_health(health_data):
    """
    Analyzes device health data for security risks.
    """
    # Placeholder for more sophisticated analysis
    if health_data.get("is_rooted"):
        return {"risk_score": 9, "is_compromised": True}
    return {"risk_score": 1, "is_compromised": False}

def analyze_network_traffic(traffic_log):
    """
    Analyzes network traffic for malicious patterns.
    """
    risk_score = 1
    is_suspicious = False
    destination_ip = traffic_log.get("destination_ip")

    if destination_ip:
        abuseipdb_results = threat_intelligence.check_ip_abuseipdb(destination_ip)
        if abuseipdb_results:
            abuse_score = abuseipdb_results.get("abuse_confidence_score", 0)
            if abuse_score > settings.abuse_confidence_score_threshold:
                risk_score = max(risk_score, 7)
                is_suspicious = True

    return {"risk_score": risk_score, "is_suspicious": is_suspicious}

def analyze_app(db: Session, app: schemas.AppCreate, all_icons: List[crud.models.Icon] = None):
    """
    Analyzes an app for clone/fake detection.
    """
    is_clone = False
    is_fake = False

    # Icon hash analysis
    if app.icon_b64:
        try:
            image_data = base64.b64decode(app.icon_b64)
            image = Image.open(io.BytesIO(image_data))
            icon_hash = average_hash(image)
            if all_icons is None:
                all_icons = crud.get_all_icons(db)
            for known_icon in all_icons:
                known_hash = hex_to_hash(known_icon.hash)
                if icon_hash - known_hash < 5: # 5 is a reasonable threshold
                    is_clone = True
                    break
        except Exception as e:
            print(f"Error processing icon: {e}")

    # Keyword analysis
    clone_keywords = ["clone", "copy", "replica", "duplicate"]
    fake_keywords = ["fake", "scam", "phishing", "malware"]
    app_name = app.name.lower()
    for keyword in clone_keywords:
        if keyword in app_name:
            is_clone = True
            break
    for keyword in fake_keywords:
        if keyword in app_name:
            is_fake = True
            break

    return {"is_clone": is_clone, "is_fake": is_fake}

def analyze_url_for_phishing(url: schemas.UrlCreate):
    """
    Analyzes a URL for phishing.
    """
    is_phishing = False
    risk_score = 0
    virustotal_results = threat_intelligence.check_url_virustotal(url.url)
    if virustotal_results:
        if virustotal_results["malicious"] > 0:
            is_phishing = True
            risk_score = 9
        elif virustotal_results["suspicious"] > 0:
            is_phishing = True
            risk_score = 6
    return {"is_phishing": is_phishing, "risk_score": risk_score}
