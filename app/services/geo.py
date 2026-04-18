import math


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Udaljenost između dvije GPS koordinate u kilometrima."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def filter_by_radius(activities, user_lat: float, user_lng: float, radius_km: float):
    """Filtrira aktivnosti po radijusu i dodaje distance_km polje."""
    result = []
    for activity in activities:
        dist = haversine_km(user_lat, user_lng, activity.lat, activity.lng)
        if dist <= radius_km:
            activity.distance_km = round(dist, 2)
            result.append(activity)
    result.sort(key=lambda a: a.distance_km)
    return result
