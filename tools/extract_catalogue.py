"""Génère catalogue.json depuis le fichier tarif Numbers Novax.

Usage : python3 tools/extract_catalogue.py "data/TARIF NOVAX 2025 CFA version 1.numbers"
Puis : python3 tools/build.py   (injecte le catalogue dans index.html)
"""
import json, sys, os
from numbers_parser import Document

GROUPES = {"CLEAR": "Blanc (clair)", "PHOTOCHROMIC": "Photochromique",
           "BLUE-BLOCK": "Filtre lumière bleue", "POLARIZED": "Polarisé"}
FAMILLES = {"PROGRESSIVES": "Progressif", "DEGRESSIVE": "Dégressif",
            "SINGLE VISION": "Unifocal", "BIFOCAL": "Bifocal"}
# Corrections de famille d'après le nom du verre (les en-têtes fusionnés du fichier
# ne couvrent pas toujours exactement les bonnes colonnes).
FAMILLE_PAR_NOM = {"Nucleo SV - Double Aspherical": "Unifocal",
                   "Drive On / Sportive PAL": "Progressif",
                   "Nexus 4D": "Progressif"}
TEINTES = {"RX Tinting": "Teinte unie", "Degrade Tinting": "Teinte dégradée",
           "Tinting by Sample": "Teinte sur échantillon", "ANTIFAR (UV400)": "Antifar (UV400)"}
OPTIONS_FR = {
    "Mdp (Midpoint)": "MDP (point milieu)", "Oval Diameter": "Diamètre ovale",
    "Diameter Reduction": "Réduction de diamètre", "Over 6 CYL": "Cylindre > 6",
    "Prism": "Prisme", "Decentration": "Décentrement",
    "Special Base/Special Thickness": "Base / épaisseur spéciale",
    "Caliber (Thickness Compensation)": "Calibrage (compensation d'épaisseur)",
    "Production by Frame": "Fabrication selon monture",
    "Frosted Glass Process": "Verre dépoli", "Standard Glass Cutting": "Taillage standard",
    "Special Glass Cutting": "Taillage spécial", "Sport Glasses Cutting": "Taillage lunettes sport",
    "Laser Custom Engraving": "Gravure laser personnalisée",
    "Therapeutic Special Filters": "Filtres thérapeutiques spéciaux",
    "FL 41 Anti Migraine": "FL 41 anti-migraine"}

def clean(v):
    return v.strip() if isinstance(v, str) else v

def prix(v):
    return int(round(v)) if isinstance(v, (int, float)) and v > 0 else None

def matrice(table, gamme, nouveau):
    rows = [[clean(c.value) for c in r] for r in table.rows()]
    head_fam, head_names = rows[0], rows[1]
    familles, fam = {}, None
    for j in range(2, len(head_names)):
        if head_fam[j]:
            fam = FAMILLES.get(head_fam[j].upper(), head_fam[j])
        familles[j] = fam
    verres = []
    groupe = None
    lignes = []
    for r in rows[2:]:
        if r[0]:
            groupe = GROUPES.get(r[0].upper(), r[0])
        if r[1]:
            lignes.append((groupe, str(r[1]), r))
    for j in range(2, len(head_names)):
        nom = head_names[j]
        if not nom:
            continue
        mats = [{"groupe": g, "matiere": m, "prix": prix(r[j])}
                for g, m, r in lignes if j < len(r) and prix(r[j])]
        if not mats:
            continue
        verres.append({"id": f"{gamme}-{j}", "nom": nom,
                       "famille": FAMILLE_PAR_NOM.get(nom, familles[j]),
                       "gamme": gamme, "nouveau": nouveau, "matieres": mats})
    return verres

def stock(table):
    rows = [[clean(c.value) for c in r] for r in table.rows()][1:]
    out, mat = [], None
    for r in rows:
        if r[0]:
            mat = str(r[0])
        p = prix(r[5])
        if not p:
            continue
        d = r[1]
        d = str(int(d)) if isinstance(d, float) else str(d)
        out.append({"groupe": mat, "matiere": f"{mat} · Ø{d} · SPH {r[2]} · {r[3]}", "prix": p})
    return [{"id": "stock", "nom": "Verres de stock", "famille": "Stock (unifocal)",
             "gamme": "Stock", "nouveau": False, "matieres": out}]

def special(table):
    rows = [[clean(c.value) for c in r] for r in table.rows()]
    options, traitements, colorations = [], [], []
    section = None
    for r in rows:
        a, b, d, e = r[0], r[1], r[3], r[4]
        if a and a not in ("Special Treatments", "Special Glasses"):
            options.append({"nom": OPTIONS_FR.get(a, a), "prix": prix(b)})
        if d:
            if d in ("Tinting", "Coating") or d.startswith("Therapeutic"):
                section = d
            elif section == "Tinting":
                colorations.append({"nom": TEINTES.get(d, d), "groupe": "Teintes", "prix": prix(e), "teinte": d != "ANTIFAR (UV400)"})
            elif section == "Coating":
                traitements.append({"nom": " ".join(d.split()), "prix": prix(e)})
            else:
                colorations.append({"nom": d, "groupe": "Filtres thérapeutiques", "prix": prix(e), "teinte": False})
    return traitements, colorations, options

def main(path):
    doc = Document(path)
    sh = {s.name.strip().upper(): s.tables[0] for s in doc.sheets}
    verres = matrice(sh["RX CFA"], "RX", False) + matrice(sh["NEW PRODUCT CFA"], "Nouveaux produits", True) + stock(sh["STOCK CFA"])
    traitements, colorations, options = special(sh["SPECIAL TREATMENT CFA"])
    cat = {"source": os.path.basename(path), "devise": "CFA", "verres": verres,
           "traitements": traitements, "colorations": colorations, "options": options}
    out = os.path.join(os.path.dirname(__file__), "..", "data", "catalogue.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False, indent=1)
    print(f"{len(verres)} verres, {len(traitements)} traitements, {len(colorations)} colorations, {len(options)} options -> {out}")

if __name__ == "__main__":
    main(sys.argv[1])
