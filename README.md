# Commande Novax

Application hors ligne pour aider les opticiens à passer leurs commandes de verres Novax.

**Parcours :** puissance (SPH / CYL / AXE / ADD par œil) → type de verre → traitement → coloration → récapitulatif → envoi sur WhatsApp (vous choisissez le destinataire).

## Utilisation

- **Sur ordinateur ou téléphone :** ouvrir `index.html` dans le navigateur. Tout le catalogue est intégré au fichier, aucune connexion n'est nécessaire (sauf pour envoyer le message WhatsApp).
- **Comme application sur téléphone :** publier le dossier (par ex. GitHub Pages), ouvrir le lien puis « Ajouter à l'écran d'accueil ». L'app reste ensuite disponible hors ligne.

## Prix

Les prix viennent du fichier `data/TARIF NOVAX 2025 CFA version 1.numbers`. Ils sont **par œil** dans le tarif ; l’app affiche directement le prix de la paire (ou d’un verre si un seul œil est commandé). Le total = (verre + traitement + coloration + options) × nombre d'yeux commandés. Les cases vides ou à 0 du tarif sont considérées comme non disponibles ; les options sans prix sont marquées « sur devis ».

## Mettre à jour le tarif

```bash
pip install numbers-parser
python3 tools/extract_catalogue.py "data/TARIF NOVAX 2025 CFA version 1.numbers"
python3 tools/build.py
```

Puis changer `VERSION` dans `sw.js` pour que les téléphones récupèrent le nouveau tarif.
