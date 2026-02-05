import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class CostAnalyzer:
    def __init__(self, df):
        self.df = df

    def plot_financial_balance(self):
        print("Génération Graphe : Bilan Financier (Est. 2025)...")
        
        required = ['Price_EUR', 'Revenue_Cumul_Million_EUR']
        if not all(col in self.df.columns for col in required):
            print(f"⚠️ Erreur : Colonnes financières manquantes ({required}). Vérifiez le Loader.")
            return

        sns.set_theme(style="whitegrid")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

        # Graphe 1 : Le Prix (Volatilité)
        # On affiche une moyenne glissante légère pour la lisibilité si besoin, ou brut
        ax1.plot(self.df.index, self.df['Price_EUR'], color='grey', lw=0.5, alpha=0.7)
        ax1.set_title("Proxy du Prix de l'Électricité (€/MWh)", fontsize=14)
        ax1.set_ylabel("Prix (€/MWh)")

        # Graphe 2 : Le Cumul (Trésor de Guerre)
        cumul = self.df['Revenue_Cumul_Million_EUR']
        
        # Couleur dynamique : Vert si on finit positif, Rouge si négatif
        final_bilan = cumul.iloc[-1]
        color_line = 'green' if final_bilan > 0 else 'red'
        
        ax2.plot(cumul.index, cumul, color=color_line, lw=2)
        
        # Remplissage vert/rouge
        ax2.fill_between(cumul.index, cumul, 0, where=(cumul > 0), color='green', alpha=0.1)
        ax2.fill_between(cumul.index, cumul, 0, where=(cumul < 0), color='red', alpha=0.1)

        ax2.set_title(f"Bilan Financier Cumulé 2025 : {final_bilan:+.1f} Millions € (Estimé)", fontsize=16, fontweight='bold')
        ax2.set_ylabel("Gain Cumulé (Millions €)")
        
        # Ligne zéro
        ax2.axhline(0, color='black', lw=1, linestyle='--')

        plt.tight_layout()
        print(f"Graphique Financier généré. Bilan final : {final_bilan:.2f} M€")
        plt.show()