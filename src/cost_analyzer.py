import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class CostAnalyzer:
    def __init__(self, df):
        self.df = df

    def plot_financial_balance(self):
        print("\n--- Génération Graphe : Bilan Financier (Prix Spot 2025) ---")
        
        # 1. Vérification des colonnes
        required = ['Price_EUR', 'Revenue_Cumul_Million_EUR']
        for col in required:
            if col not in self.df.columns:
                print(f"❌ ERREUR : Colonne '{col}' manquante dans le DataFrame.")
                return

        # 2. Vérification des données (Debug)
        avg_price = self.df['Price_EUR'].mean()
        final_balance = self.df['Revenue_Cumul_Million_EUR'].iloc[-1]
        print(f"   [DEBUG] Prix Spot Moyen : {avg_price:.2f} €/MWh")
        print(f"   [DEBUG] Bilan Final : {final_balance:.2f} Millions €")

        if avg_price == 0:
            print("⚠️ ALERTE : Le prix moyen est 0. Le graphe sera plat.")
        
        if pd.isna(final_balance):
            print("⚠️ ALERTE : Le bilan final est NaN (Vide). Vérifie les données d'entrée.")
            # Tentative de sauvetage : on remplace les NaN par 0 pour le tracé
            self.df['Revenue_Cumul_Million_EUR'] = self.df['Revenue_Cumul_Million_EUR'].fillna(0)

        # 3. Tracé
        sns.set_theme(style="whitegrid")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

        # --- Graphe 1 : Le Prix Spot (Journalier pour lisibilité) ---
        # On resample par jour pour éviter le bruit horaire illisible sur un an
        daily_price = self.df['Price_EUR'].resample('D').mean()
        
        ax1.plot(daily_price.index, daily_price, color='#2c3e50', lw=1.5, label="Prix Spot Moyen (Jour)")
        ax1.fill_between(daily_price.index, daily_price, color='#2c3e50', alpha=0.1)
        
        ax1.set_title("Prix de l'Électricité Spot Suisse (2025)", fontsize=14, fontweight='bold')
        ax1.set_ylabel("Prix (€/MWh)")
        ax1.legend(loc="upper right")
        ax1.grid(True, which='both', linestyle='--', alpha=0.5)

        # --- Graphe 2 : Le Cumul Financier ---
        cumul = self.df['Revenue_Cumul_Million_EUR']
        
        # On détermine la couleur finale
        final_val = cumul.iloc[-1]
        color_line = '#27ae60' if final_val > 0 else '#e74c3c' # Vert ou Rouge
        
        ax2.plot(cumul.index, cumul, color=color_line, lw=2.5, label="Gain Cumulé")
        
        # Zones positives (Vert) et négatives (Rouge)
        ax2.fill_between(cumul.index, cumul, 0, where=(cumul >= 0), color='#2ecc71', alpha=0.2, interpolate=True)
        ax2.fill_between(cumul.index, cumul, 0, where=(cumul < 0), color='#e74c3c', alpha=0.2, interpolate=True)

        ax2.set_title(f"Bilan Financier Cumulé : {final_val:+.1f} Millions €", fontsize=16, fontweight='bold')
        ax2.set_ylabel("Gain Cumulé (Millions €)")
        ax2.axhline(0, color='black', lw=1, linestyle='--')
        
        # Annotations (Optionnel mais classe)
        min_val = cumul.min()
        min_date = cumul.idxmin()
        if not pd.isna(min_val):
             ax2.annotate(f'Creux Hivernal\n({min_val:.0f} M€)', 
                         xy=(min_date, min_val), 
                         xytext=(min_date, min_val - 200),
                         arrowprops=dict(facecolor='black', shrink=0.05),
                         ha='center', fontsize=10)

        plt.tight_layout()        
        plt.show()