from datetime import datetime
import socket
import subprocess
import platform
import re
import tkinter as tk
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


def date():
    jour = datetime.now()
    return f"Rapport généré le {jour.strftime('%A %d %B %Y à %H:%M:%S')}"                            


def nom_hote():
    return f"Ce rapport a été généré sur la machine de {socket.gethostname()}"


def version_noyau():
    return f"Version du noyau Linux : {platform.release()}"


def temps_fonctionnement_system():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        return uptime_seconds

def convertir_temps(secondes):
    jours = int(secondes // (24 * 3600))
    reste = secondes % (24 * 3600)
    heures = int(reste // 3600)
    reste %= 3600
    minutes = int(reste // 60)
    secondes_restantes = int(reste % 60)
    return f"{jours} jours, {heures} heures, {minutes} minutes, {secondes_restantes} secondes"

def temps_fonctionnement_system_general():
    secondes = temps_fonctionnement_system()
    return f"Durée de fonctionnement du système : { convertir_temps(secondes)}"


def temperature_cpu():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_milli = int(f.read().strip())
        return f"Température du CPU : {temp_milli / 1000:.1f}°C"
    except:
        return "Température CPU non disponible"


def alimentation():
    try:
        with open("/sys/class/power_supply/BAT0/status", "r") as f:
            etat = f.read().strip()
        with open("/sys/class/power_supply/BAT0/capacity", "r") as f:
            niveau = f.read().strip()
        etat_fr = {
            "Charging": "En charge",
            "Discharging": "Sur batterie",
            "Full": "Chargée"
        }.get(etat, "État inconnu")
        return(f"L'état de la batterie: Batterie : {niveau}% ({etat_fr})")
    except:
        return("Batterie non détectée ou inaccessible")


def mémoire_vive():
    try:
        meminfo = {}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split(":")
                key = parts[0]
                value = parts[1].strip().split()[0]
                meminfo[key] = int(value)  

        total = meminfo.get("MemTotal", 0)
        available = meminfo.get("MemAvailable", 0)
        cache = meminfo.get("Cached", 0)
        used = total - available

        # Calcul en pourcentage
        percent_total = 100.0 if total else 0.0
        percent_used = (used / total) * 100 if total else 0
        percent_available = (available / total) * 100 if total else 0
        percent_cache = (cache / total) * 100 if total else 0

        return (
            f"<tr><td>Total</td><td>{percent_total:.1f} %</td></tr>"
            f"<tr><td>Utilisée</td><td>{percent_used:.1f}%</td></tr>"
            f"<tr><td>Disponible</td><td>{percent_available:.1f}%</td></tr>"
            f"<tr><td>Cache</td><td>{percent_cache:.1f}%</td></tr>"
        )
    except Exception as e:
        return f"<tr><td>Erreur mémoire</td><td>{str(e)}</td></tr>"

def mémoire_vive_texte():
    try:
        meminfo = {}
        with open("/proc/meminfo", "r") as f:
            for line in f:
                parts = line.split(":")
                key = parts[0]
                value = parts[1].strip().split()[0]
                meminfo[key] = int(value)
        total = meminfo.get("MemTotal", 0)
        available = meminfo.get("MemAvailable", 0)
        cache = meminfo.get("Cached", 0)
        used = total - available
        percent_used = (used / total) * 100 if total else 0

        return (
            f"Total: {total // 1024} MB\n"
            f"Utilisée: {used // 1024} MB\n"
            f"Disponible: {available // 1024} MB\n"
            f"Cache: {cache // 1024} MB\n"
            f"Utilisation: {percent_used:.1f}%"
        )
    except Exception as e:
        return f"Erreur mémoire: {str(e)}"

    


def stockage_disque(path="/"):
    try:
        result = subprocess.run(["df", "-k", path], capture_output=True, text=True)
        lignes = result.stdout.strip().split("\n")
        if len(lignes) < 2:
            return "<tr><td>Erreur</td><td>Impossible de lire les infos disque</td></tr>"
        parts = lignes[1].split()
        total = int(parts[1]) // 1024
        utilisé = int(parts[2]) // 1024
        dispo = int(parts[3]) // 1024
        pourcentage = parts[4]

        return (
            f"<tr><td>Total</td><td>{total} Mo</td></tr>"
            f"<tr><td>Utilisé</td><td>{utilisé} Mo</td></tr>"
            f"<tr><td>Disponible</td><td>{dispo} Mo</td></tr>"
            f"<tr><td>Utilisation</td><td>{pourcentage}</td></tr>"
        )
    except Exception as e:
        return f"<tr><td>Erreur disque</td><td>{str(e)}</td></tr>"


def stockage_disque_texte(path="/"):
    try:
        result = subprocess.run(["df", "-k", path], capture_output=True, text=True)
        lignes = result.stdout.strip().split("\n")
        if len(lignes) < 2:
            return "Erreur: Impossible de lire les infos disque"
        parts = lignes[1].split()
        total = int(parts[1]) // 1024
        utilisé = int(parts[2]) // 1024
        dispo = int(parts[3]) // 1024
        pourcentage = parts[4]
        
        return (
            f"Total: {total} Mo\n"
            f"Utilisé: {utilisé} Mo\n"
            f"Disponible: {dispo} Mo\n"
            f"Utilisation: {pourcentage}"
        )
    except Exception as e:
        return f"Erreur disque : {e}"
    

def get_processus_actifs(n=10):
    try:
        result = subprocess.run(
            ["ps", "-eo", "pid,user:20,comm:30,%mem,%cpu", "--sort=-%mem", "--no-headers"],
            capture_output=True, text=True
        )
        lignes = result.stdout.strip().split("\n")[:n]
        lignes_html = ""
        
        for ligne in lignes:
            parts = ligne.split()
            if len(parts) >= 5:
                pid = parts[0]
                user = parts[1]
                cpu = parts[-1]
                mem = parts[-2]
                nom = ' '.join(parts[2:-2])
                
                lignes_html += f"<tr><td>{pid}</td><td>{user}</td><td>{nom}</td><td>{mem}%</td><td>{cpu}%</td></tr>\n"
        
        return lignes_html if lignes_html else "<tr><td colspan='5'>Aucun processus trouvé</td></tr>"
    except Exception as e:
        return f"<tr><td colspan='5'>Erreur processus : {str(e)}</td></tr>"


def get_interfaces_info():
    try:
        output = subprocess.check_output(['ip', 'addr'], text=True)
        interfaces = {}
        current_iface = None

        for line in output.splitlines():
            match_iface = re.match(r'\d+: (\w+):', line)
            if match_iface:
                current_iface = match_iface.group(1)
                interfaces[current_iface] = {}
            elif 'inet ' in line and current_iface:
                match_ip = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/(\d+)', line)
                if match_ip:
                    interfaces[current_iface]['Adresse IP'] = match_ip.group(1)
                    interfaces[current_iface]['Masque CIDR'] = match_ip.group(2)

        return interfaces

    except subprocess.CalledProcessError as e:
        return {'Erreur': str(e)}
    


def afficher_interfaces():
    interfaces = get_interfaces_info()
    html = ""
    for iface, details in interfaces.items():
        for key, value in details.items():
            html += f"<tr><td>{iface}</td><td>{key}</td><td>{value}</td></tr>\n"
    return html if html else "<tr><td colspan='3'>Aucune interface détectée</td></tr>"



def services_web():
    services = []
    ports = [(80, "http"), (443, "https")]
    
    for port, protocol in ports:
        service_info = {
            'port': port,
            'protocol': protocol.upper(),
            'status': 'Fermé',
            'titre': 'N/A',
            'serveur': 'N/A',
            'favicon': 'N/A',
            'code_http': 'N/A'
        }
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        
        if result == 0:
            service_info['status'] = 'Ouvert'
            
            try:
                url = f"{protocol}://localhost:{port}"
                req = Request(url)
                req.add_header('User-Agent', 'SupKrellM/1.0')
                response = urlopen(req, timeout=3)
                
                service_info['code_http'] = response.getcode()
                
                if 'Server' in response.headers:
                    service_info['serveur'] = response.headers['Server']
                
                html_content = response.read().decode('utf-8', errors='ignore')
                
                match_title = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
                if match_title:
                    service_info['titre'] = match_title.group(1).strip()
                
                match_favicon = re.search(r'<link[^>]*rel=["\'](?:shortcut )?icon["\'][^>]*href=["\'](.*?)["\']', html_content, re.IGNORECASE)
                if match_favicon:
                    service_info['favicon'] = match_favicon.group(1)
                
            except HTTPError as e:
                service_info['code_http'] = e.code
                if hasattr(e, 'headers') and 'Server' in e.headers:
                    service_info['serveur'] = e.headers['Server']
            except:
                pass
        
        sock.close()
        services.append(service_info)
    
    return services

def afficher_services_web():
    services = services_web()
    html = ""
    
    for service in services:
        html += f"<tr>"
        html += f"<td>{service['port']}</td>"
        html += f"<td>{service['protocol']}</td>"
        html += f"<td>{service['status']}</td>"
        html += f"<td>{service['code_http']}</td>"
        html += f"<td>{service['serveur']}</td>"
        html += f"<td>{service['titre']}</td>"
        html += f"<td>{service['favicon']}</td>"
        html += f"</tr>\n"
    
    return html if html else "<tr><td colspan='7'>Aucun service web détecté</td></tr>"



def generate_rapport_html():
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport Système</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Rapport Système</h1>
    <p><em>{date()}</em></p>

    <h2>Informations Générales</h2>
    <ul>
        <li>{nom_hote()}</li>
        <li>{version_noyau()}</li>
        <li>{temps_fonctionnement_system_general()}</li>
    </ul>

    <h2>Température CPU</h2>
    <ul>
        <li>{temperature_cpu()}</li>
        <li>{alimentation()}</li>
    </ul>
    <h2>Mémoire Vive</h2>
    <table>
    
        <thead>
            <tr><th>Paramètre</th><th>Valeur</th></tr>
        </thead>
        <tbody>
       
            {mémoire_vive()}
       
        </tbody>
    </table>
       

    <h2>Stockage Disque</h2>
    <table>
    
        <thead>
            <tr><th>Paramètre</th><th>Valeur</th></tr>
        </thead>
        <tbody>
        
            {stockage_disque()}
       
        </tbody>
    </table>
    
    <h2>Processus Actifs</h2>
    <table>
        <thead>
            <tr><th>PID</th><th>User</th><th>Nom</th><th>Mémoire</th><th>CPU</th></tr>
        </thead>
        <tbody>
            {get_processus_actifs()}
        </tbody>
    </table>
    
    <h2>Interfaces Réseau</h2>
    <table>
        <thead>
            <tr><th>Interface</th><th>Clé</th><th>Valeur</th></tr>
        </thead>
        <tbody>
            {afficher_interfaces()}
        </tbody>
    </table>

    <h2>Services Web (Ports 80/443)</h2>
    <table>
        <thead>
            <tr><th>Port</th><th>Protocole</th><th>Status</th><th>Code HTTP</th><th>Serveur</th><th>Titre</th><th>Favicon</th></tr>
        </thead>
        <tbody>
            {afficher_services_web()}
        </tbody>
    </table>

</body>
</html>"""

    with open("rapport.html", "w", encoding="utf-8") as f:
        f.write(html)

def generer_rapport_html_selectif(selected):
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport Système</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Rapport Système</h1>
    <p><em>{date()}</em></p>
"""
    
    if 'infos' in selected:
        html += f"""
    <h2>Informations Générales</h2>
    <ul>
        <li>{nom_hote()}</li>
        <li>{version_noyau()}</li>
        <li>{temps_fonctionnement_system_general()}</li>
    </ul>
"""
    
    if 'temperature' in selected:
        html += f"""
    <h2>Température CPU</h2>
    <ul>
        <li>{temperature_cpu()}</li>
        <li>{alimentation()}</li>
    </ul>
"""
    
    if 'memoire' in selected:
        html += f"""
    <h2>Mémoire Vive</h2>
    <table>
        <thead><tr><th>Paramètre</th><th>Valeur</th></tr></thead>
        <tbody>{mémoire_vive()}</tbody>
    </table>
"""
    
    if 'disque' in selected:
        html += f"""
    <h2>Stockage Disque</h2>
    <table>
        <thead><tr><th>Paramètre</th><th>Valeur</th></tr></thead>
        <tbody>{stockage_disque()}</tbody>
    </table>
"""
    
    if 'processus' in selected:
        html += f"""
    <h2>Processus Actifs</h2>
    <table>
        <thead><tr><th>PID</th><th>User</th><th>Nom</th><th>Mémoire</th><th>CPU</th></tr></thead>
        <tbody>{get_processus_actifs()}</tbody>
    </table>
"""
    
    if 'reseau' in selected:
        html += f"""
    <h2>Interfaces Réseau</h2>
    <table>
        <thead><tr><th>Interface</th><th>Clé</th><th>Valeur</th></tr></thead>
        <tbody>{afficher_interfaces()}</tbody>
    </table>
"""
    
    if 'web' in selected:
        html += f"""
    <h2>Services Web (Ports 80/443)</h2>
    <table>
        <thead><tr><th>Port</th><th>Protocole</th><th>Status</th><th>Code HTTP</th><th>Serveur</th><th>Titre</th><th>Favicon</th></tr></thead>
        <tbody>{afficher_services_web()}</tbody>
    </table>
"""
    
    html += """
</body>
</html>"""
    return html


 
def lancer_interface():
    rapport = tk.Tk()
    rapport.geometry("800x600")
    rapport.title("Rapport système")
    canvas = tk.Canvas(rapport)
    scrollbar = tk.Scrollbar(rapport, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    label_titre = tk.Label(scrollable_frame, text="Rapport Système", font=("Arial", 20, "bold"), fg="#003366")
    label_titre.pack(pady=10)
    
    frame_infos = tk.LabelFrame(scrollable_frame, text="Informations Générales", padx=10, pady=10, font=("Arial", 12, "bold"))
    frame_infos.pack(fill="x", padx=20, pady=10)

    label_date = tk.Label(frame_infos, text=date(), anchor="w", justify="left")
    label_date.pack(fill="x")

    label_hote = tk.Label(frame_infos, text=nom_hote(), anchor="w", justify="left")
    label_hote.pack(fill="x")

    label_noyau = tk.Label(frame_infos, text=version_noyau(), anchor="w", justify="left")
    label_noyau.pack(fill="x")

    label_uptime = tk.Label(frame_infos, text=temps_fonctionnement_system_general(), anchor="w", justify="left")
    label_uptime.pack(fill="x")

    frame_temp = tk.LabelFrame(scrollable_frame, text="Température et Alimentation", padx=10, pady=10, font=("Arial", 12, "bold"))
    frame_temp.pack(fill="x", padx=20, pady=10)

    label_temp = tk.Label(frame_temp, text=temperature_cpu(), anchor="w", justify="left")
    label_temp.pack(fill="x")

    label_batterie = tk.Label(frame_temp, text=alimentation(), anchor="w", justify="left")
    label_batterie.pack(fill="x")

    frame_memoire = tk.LabelFrame(scrollable_frame, text="Mémoire Vive", padx=10, pady=10, font=("Arial", 12, "bold"))
    frame_memoire.pack(fill="x", padx=20, pady=10)

    label_memoire = tk.Label(frame_memoire, text=mémoire_vive(), anchor="w", justify="left")
    label_memoire.pack(fill="x")

    frame_stockage = tk.LabelFrame(scrollable_frame, text="Stockage Disque", padx=10, pady=10, font=("Arial", 12, "bold"))
    frame_stockage.pack(fill="x", padx=20, pady=10)

    label_stockage = tk.Label(frame_stockage, text=stockage_disque(), anchor="w", justify="left")
    label_stockage.pack(fill="x")

    frame_processus = tk.LabelFrame(scrollable_frame, text="Processus Actifs", padx=10, pady=10, font=("Arial", 12, "bold"))
    frame_processus.pack(fill="x", padx=20, pady=10)

    headers = ["PID", "User" , "Nom", "Mémoire", "CPU"]
    for i, h in enumerate(headers):
        tk.Label(frame_processus, text=h, font=("Arial", 10, "bold"), borderwidth=1, relief="solid", width=15).grid(row=0, column=i)

    lignes_html = get_processus_actifs().split("\n")
    for row_index, ligne in enumerate(lignes_html, start=1):
        if "<td>" in ligne:
            valeurs = re.findall(r"<td>(.*?)</td>", ligne)
            for col_index, val in enumerate(valeurs):
                tk.Label(frame_processus, text=val, borderwidth=1, relief="solid", width=15).grid(row=row_index, column=col_index)

    
    frame_reseau = tk.LabelFrame(scrollable_frame, text="Interfaces Réseau", padx=10, pady=10, font=("Arial", 12, "bold"))
    frame_reseau.pack(fill="x", padx=20, pady=10)

    headers = ["Interface", "Clé", "Valeur"]
    for i, h in enumerate(headers):
        tk.Label(frame_reseau, text=h, font=("Arial", 10, "bold"), borderwidth=1, relief="solid", width=20).grid(row=0, column=i)

    lignes_html = afficher_interfaces().split("\n")
    for row_index, ligne in enumerate(lignes_html, start=1):
        if "<td>" in ligne:
            valeurs = re.findall(r"<td>(.*?)</td>", ligne)
            for col_index, val in enumerate(valeurs):
                tk.Label(frame_reseau, text=val, borderwidth=1, relief="solid", width=20).grid(row=row_index, column=col_index)


    frame_services = tk.LabelFrame(scrollable_frame, text="Services Web (Ports 80/443)", padx=10, pady=10, font=("Arial", 12, "bold"))
    frame_services.pack(fill="x", padx=20, pady=10)

    headers = ["Port", "Protocole", "Status", "Code HTTP", "Serveur", "Titre", "Favicon"]
    for i, h in enumerate(headers):
        tk.Label(frame_services, text=h, font=("Arial", 10, "bold"), borderwidth=1, relief="solid", width=12).grid(row=0, column=i)

    lignes_html = afficher_services_web().split("\n")
    for row_index, ligne in enumerate(lignes_html, start=1):
        if "<td>" in ligne:
            valeurs = re.findall(r"<td>(.*?)</td>", ligne)
            for col_index, val in enumerate(valeurs):
                tk.Label(frame_services, text=val, borderwidth=1, relief="solid", width=12).grid(row=row_index, column=col_index)


    

    def mettre_à_jour():
        label_date.config(text=date())
        label_hote.config(text=nom_hote())
        label_noyau.config(text=version_noyau())
        label_uptime.config(text=temps_fonctionnement_system_general())
        label_temp.config(text=temperature_cpu())
        label_batterie.config(text=alimentation())
        label_memoire.config(text=mémoire_vive_texte())
        label_stockage.config(text=(stockage_disque_texte()))

   

        
        for widget in frame_processus.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        lignes_html = get_processus_actifs().split("\n")
        for row_index, ligne in enumerate(lignes_html, start=1):
            if "<td>" in ligne:
                valeurs = re.findall(r"<td>(.*?)</td>", ligne)
                for col_index, val in enumerate(valeurs):
                    tk.Label(frame_processus, text=val, borderwidth=1, relief="solid", width=15).grid(row=row_index, column=col_index)

       
        for widget in frame_reseau.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        lignes_html = afficher_interfaces().split("\n")
        for row_index, ligne in enumerate(lignes_html, start=1):
            if "<td>" in ligne:
                valeurs = re.findall(r"<td>(.*?)</td>", ligne)
                for col_index, val in enumerate(valeurs):
                    tk.Label(frame_reseau, text=val, borderwidth=1, relief="solid", width=20).grid(row=row_index, column=col_index)


        for widget in frame_services.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        lignes_html = afficher_services_web().split("\n")
        for row_index, ligne in enumerate(lignes_html, start=1):
            if "<td>" in ligne:
                valeurs = re.findall(r"<td>(.*?)</td>", ligne)
                for col_index, val in enumerate(valeurs):
                    tk.Label(frame_services, text=val, borderwidth=1, relief="solid", width=12).grid(row=row_index, column=col_index)
        
        rapport.after(2000, mettre_à_jour)

    mettre_à_jour() 
    rapport.mainloop()


if __name__ == "__main__":
    import sys
    import argparse
    from pathlib import Path
    import shutil
    
    parser = argparse.ArgumentParser(description='SupKrellM - Moniteur système Linux')
    
    parser.add_argument('--gui', action='store_true', help='Lancer l\'interface graphique')
    parser.add_argument('--output', '-o', default='rapport.html', help='Nom du fichier de sortie')
    parser.add_argument('--dir', '-d', default='.', help='Dossier de destination')
    parser.add_argument('--metrics', '-m', help='Métriques à inclure (infos,cpu,memoire,disque,processus,interfaces,services) - toutes par défaut')
    
    args = parser.parse_args()
    
    if args.gui:
        lancer_interface()
    else:
        if args.metrics:
            selected = args.metrics.split(',')
        else:
            selected = ['infos', 'cpu', 'memoire', 'disque', 'processus', 'interfaces', 'web']
        
        dossier = Path(args.dir)
        
        if args.dir != '.' and not dossier.exists():
            try:
                dossier.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Erreur création dossier : {e}")
                sys.exit(1)
        
        chemin_fichier = dossier / args.output
        
        html_content = generer_rapport_html_selectif(selected)
        
        with open("rapport.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        if args.dir != '.':
            try:
                shutil.move('rapport.html', str(chemin_fichier))
                print(f"Rapport HTML généré : {chemin_fichier}")
            except Exception as e:
                print(f"Erreur déplacement : {e}")
        else:
            if args.output != 'rapport.html':
                try:
                    shutil.move('rapport.html', args.output)
                    print(f"Rapport HTML généré : {args.output}")
                except Exception as e:
                    print(f"Erreur : {e}")
            else:
                print("Rapport HTML généré : rapport.html")