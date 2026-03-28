import math
from datetime import datetime, timedelta, timezone
import gpxpy
import gpxpy.gpx

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance en mètres entre deux coordonnées GPS."""
    R = 6371000  # Rayon de la Terre en mètres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def generer_gpx(waypoints, allure_min_km, heure_depart):
    """Génère un fichier GPX avec interpolation des points à la seconde."""
    
    # Calcul de la vitesse en mètres par seconde
    # Vitesse = Distance / Temps
    vitesse_m_s = 1000 / (allure_min_km * 60)
    
    gpx = gpxpy.gpx.GPX()
    piste = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(piste)
    segment = gpxpy.gpx.GPXTrackSegment()
    piste.segments.append(segment)

    temps_actuel = heure_depart
    
    print(f"Génération en cours... Allure cible : {allure_min_km} min/km ({vitesse_m_s:.2f} m/s)")

    for i in range(len(waypoints) - 1):
        p1 = waypoints[i]
        p2 = waypoints[i+1]
        
        # Distance entre les deux points de passage
        distance_segment = haversine_distance(p1[0], p1[1], p2[0], p2[1])
        
        # Combien de secondes faut-il pour parcourir ce segment ?
        temps_segment_secondes = distance_segment / vitesse_m_s
        nb_points = int(temps_segment_secondes) # 1 point = 1 seconde
        
        # Interpolation des points intermédiaires
        for j in range(nb_points):
            fraction = j / nb_points
            lat_interp = p1[0] + (p2[0] - p1[0]) * fraction
            lon_interp = p1[1] + (p2[1] - p1[1]) * fraction
            
            segment.points.append(gpxpy.gpx.GPXTrackPoint(
                latitude=lat_interp, 
                longitude=lon_interp, 
                time=temps_actuel
            ))
            temps_actuel += timedelta(seconds=1)
            
    # Ajout du tout dernier point exact
    segment.points.append(gpxpy.gpx.GPXTrackPoint(
        latitude=waypoints[-1][0], 
        longitude=waypoints[-1][1], 
        time=temps_actuel
    ))

    return gpx.to_xml()

# ==========================================
# ZONE DE TEST DU SCRIPT
# ==========================================
if __name__ == "__main__":
    # Liste de coordonnées GPS (Exemple : une ligne droite fictive)
    # [Latitude, Longitude]
    mes_points = [
        [48.8566, 2.3522], # Point de départ (Paris Centre)
        [48.8580, 2.3550], # Point intermédiaire
        [48.8600, 2.3600]  # Point d'arrivée
    ]
    
    allure_cible = 3.00 # 3'00"/km
    debut_course = datetime(2026, 3, 28, 9, 0, 0, tzinfo=timezone.utc)
    
    # Génération du XML
    gpx_data = generer_gpx(mes_points, allure_cible, debut_course)
    
    # Sauvegarde dans un fichier
    with open("course_simulee.gpx", "w") as f:
        f.write(gpx_data)
        
    print("Succès ! Le fichier 'course_simulee.gpx' a été créé.")
