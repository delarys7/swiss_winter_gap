# 🇨🇭 Swiss Winter Gap Analyzer

**Analyse de données et modélisation du déficit énergétique hivernal suisse.**

Ce projet Python analyse les données réelles du gestionnaire de réseau **Swissgrid** pour visualiser le phénomène du "Winter Gap" : la dépendance structurelle de la Suisse aux importations d'électricité en hiver, opposée à sa surproduction estivale.

---

## 🎯 Objectifs du Projet
1.  **Ingestion de Données :** Pipeline ETL pour traiter les fichiers bruts Swissgrid (Excel/CSV) avec une résolution de 15 minutes.
2.  **Modélisation :** Comparaison entre un modèle théorique (sinusoïdal) et la réalité physique 2024-2025.
3.  **Visualisation :** Mise en évidence des périodes critiques (Déficits) et analyse des flux transfrontaliers.

---

## 📊 Résultats Clés (Données 2025)
* **Déficit Hivernal (Winter Gap) :** La consommation dépasse la production dès novembre, nécessitant des imports massifs (> 4 GW en pointe).
* **Volatilité :** L'analyse brute montre l'extrême flexibilité de l'hydraulique suisse (stockage) pour répondre aux pics de prix journaliers.
* **L'Effet "Noël" :** Une chute volontaire de la production (~30%) est observée fin décembre, correspondant à une stratégie économique de conservation de l'eau (réservoirs) pendant la baisse de la demande industrielle européenne.

---

## 🛠️ Architecture Technique

Le projet est structuré selon les bonnes pratiques de développement (Separation of Concerns) :

```text
swiss_winter_gap/
│
├── data/                  # Stockage des fichiers sources Swissgrid (.xlsx)
├── src/
│   ├── loader.py          # Extraction & Nettoyage (Pandas, Gestion des formats de date/colonnes)
│   ├── generator.py       # Modélisation mathématique (Simulation sinusoïdale théorique)
│   ├── analyzer.py        # Logique métier (Calculs Déficit, Aggregats horaires)
│   ├── visualizer.py      # Moteur de rendu graphique (Matplotlib/Seaborn, Lissage Moving Average)
│   └── border_analysis.py # Analyse des flux Import/Export par frontière
│
├── main_real.py           # Point d'entrée pour l'analyse des Données Réelles
├── main_simu.py           # Point d'entrée pour la Simulation
└── requirements.txt       # Dépendances Python

---

## 🚀 Comment Lancer le Projet

1. Installation : Cloner le dépôt et installer les dépendances.

* git clone [https://github.com/delarys7/swiss_winter_gap.git](https://github.com/delarys7/swiss_winter_gap.git)
* pip install -r requirements.txt

2. Données

Télécharger le fichier "Energy Statistic Switzerland" depuis Swissgrid Grid Data et le placer dans le dossier data/.

3. Exécution

Pour visualiser l'analyse sur les données réelles (Attention à bien adapter le code pour utiliser les fichiers que vous voulez):
python main_real.py

---

## 📈 Méthodologie & Hypothèses

* Conversion Énergie/Puissance : Les données sources sont en énergie (kWh) sur 15 min. Elles sont rééchantillonnées en puissance moyenne horaire (MW).

* Lissage (Smoothing) : Une moyenne mobile centrée sur 7 jours (168h) est appliquée pour les graphiques de tendance afin de gommer la saisonnalité hebdomadaire (Week-end vs Semaine).

* Traitement des valeurs manquantes : Les effets de bord (fin d'année) liés au lissage sont identifiés et documentés.

---

## 👤 Auteur
Projet réalisé dans le cadre d'une analyse sectorielle du marché de l'énergie (Gap Hivernal & Frais Transfrontaliers).