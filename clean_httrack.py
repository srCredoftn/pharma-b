import os
import re
import shutil
from concurrent.futures import ThreadPoolExecutor

# === Configuration ===
BASE_DIR = "/Users/credoftn/Downloads/Pharmacie/pharma-b"  # ← ton projet
MAX_THREADS = 8
REAL_INDEX = os.path.join(BASE_DIR, "vrai_index.html")  # ← ton vrai index

# === Expressions HTTrack à supprimer dans HTML ===
patterns = [
    re.compile(r"<!--\s*Mirrored from.*?-->", re.DOTALL),
    re.compile(r"<!--\s*Added by HTTrack.*?-->", re.DOTALL),
    re.compile(r"<!--\s*Thanks for using HTTrack.*?-->", re.DOTALL),
    re.compile(r"<meta[^>]*name=[\"']generator[\"'][^>]*HTTrack[^>]*>", re.IGNORECASE),
    re.compile(r"<meta[^>]*http-equiv=[\"']content-type[\"'][^>]*>", re.IGNORECASE),
    re.compile(r'<meta http-equiv=["\']refresh["\'][^>]*>', re.IGNORECASE),
    re.compile(r'<iframe[^>]*src=["\'].*httrack.*["\'][^>]*>', re.IGNORECASE)
]

# === Nettoyage HTML ===
def clean_html(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except:
        return None

    original_content = content
    for pattern in patterns:
        content = re.sub(pattern, "", content)

    if content != original_content:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return file_path
        except:
            return None
    return None

# === Supprimer fichiers HTTrack / temporaires / backups ===
def remove_httrack_files():
    removed = []

    # Dossiers HTTrack
    for folder in [".httrack", ".hts-cache"]:
        path = os.path.join(BASE_DIR, folder)
        if os.path.exists(path):
            shutil.rmtree(path)
            removed.append(path)

    # Fichiers temporaires et logs
    for root, _, files in os.walk(BASE_DIR):
        for f in files:
            if f.endswith((".tmp", ".bak", "hts-log.txt")):
                path = os.path.join(root, f)
                os.remove(path)
                removed.append(path)

    # Supprimer index HTTrack
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        try:
            with open(index_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if "HTTrack Website Copier" in content:
                os.remove(index_path)
                removed.append(index_path)
        except:
            pass

    # Restaurer ton vrai index.html
    if os.path.exists(REAL_INDEX):
        shutil.copy(REAL_INDEX, os.path.join(BASE_DIR, "index.html"))
        removed.append("index.html remplacé par le vrai index")

    return removed

# === Parcours des fichiers HTML ===
html_files = []
for root, _, files in os.walk(BASE_DIR):
    for f in files:
        if f.endswith(".html"):
            html_files.append(os.path.join(root, f))

# === Nettoyage multi-thread ===
modified_files = []
with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    results = executor.map(clean_html, html_files)
    for r in results:
        if r:
            modified_files.append(r)

# === Supprimer fichiers HTTrack et temporaires ===
removed_files = remove_httrack_files()

# === Vérification post-nettoyage ===
remaining_traces = []
for file_path in html_files:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for pattern in patterns:
            if pattern.search(content):
                remaining_traces.append(file_path)
                break
    except:
        continue

# === Résumé final ===
print("\n========== NETTOYAGE COMPLET & PRÊT GITHUB ==========")
print(f"🔍 Fichiers HTML trouvés : {len(html_files)}")
print(f"✅ Fichiers nettoyés : {len(modified_files)}")

if removed_files:
    print("\n🗑️ Fichiers HTTrack / temporaires supprimés ou index remplacé :")
    for f in removed_files:
        print(" -", f)

if remaining_traces:
    print("\n⚠️ ATTENTION : Certaines traces HTTrack restent dans :")
    for f in remaining_traces:
        print(" -", f)
else:
    print("\n🎉 Aucun fichier ne contient plus de traces HTTrack ! Projet prêt pour GitHub.")

print("\n💡 Tu peux maintenant faire :\n")
print("git add .")
print("git commit -m 'Site nettoyé HTTrack - prêt pour GitHub'")
print("git push origin main")
