import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class CostAnalyzer:
    def __init__(self, df):
        self.df = df

    def plot_financial_balance(self):
        print("Analyse Financière (Estimation via Proxy Prix)...")
        
        # 1. Identification des colonnes
        # On cherche les colonnes "Import", "Export"
        col_import = next((c for c in self.df.columns if str(c).strip() == "Import"), None)
        col_export = next((c for c in self.df.columns if str(c).strip() == "Export"), None)
        
        # On cherche les colonnes Prix (Proxy : Prix de réglage secondaire)
        # Colonne T/V/W approx. On cherche par mots-clés "positive" et "negative"
        col_price_pos = next((c for c in self.df.columns if "positive" in str(c).lower() and "preise" in str(c).lower()), None)
        col_price_neg = next((c for c in self.df.columns if "negative" in str(c).lower() and "preise" in str(c).lower()), None)
        
        if not all([col_import, col_export, col_price_pos, col_price_neg]):
            print("⚠️ Impossible de faire l'analyse financière (Colonnes manquantes).")
            return

        # 2. Construction du Prix Proxy (Moyenne Positif/Négatif)
        # C'est une estimation brute du "Prix du Marché" à cet instant
        price_proxy = (self.df[col_price_pos] + self.df[col_price_neg]) / 2
        
        # On remplit les trous éventuels (forward fill)
        price_proxy = price_proxy.fillna(method='ffill')

        # 3. Calcul du Bilan Horaire (€)
        # Bilan = (Export * Prix) - (Import * Prix)
        # Export rapporte (+), Import coûte (-)
        
        # On travaille en ÉNERGIE (MWh) par heure
        energy_import_mwh = self.df[col_import].resample('h').sum() / 1000
        energy_export_mwh = self.df[col_export].resample('h').sum() / 1000
        avg_price_hourly = price_proxy.resample('h').mean()
        
        # Revenu Net (€) = (Ventes - Achats)
        net_revenue_euro = (energy_export_mwh - energy_import_mwh) * avg_price_hourly
        
        # Cumul annuel (Pour voir si on finit l'année riche ou pauvre)
        cumulative_revenue_million = net_revenue_euro.cumsum() / 1_000_000 # En Millions d'Euros

        # 4. Visualisation
        sns.set_theme(style="whitegrid")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

        # Graphe 1 : Le Prix Proxy (Pour voir la volatilité)
        ax1.plot(avg_price_hourly.index, avg_price_hourly, color='grey', lw=0.5, alpha=0.7)
        ax1.set_title("Proxy du Prix de l'Électricité (€/MWh)", fontsize=14)
        ax1.set_ylabel("Prix (€/MWh)")

        # Graphe 2 : Le Trésor de Guerre (Cumul)
        # Si la courbe finit positive > La Suisse a gagné de l'argent
        color_line = 'green' if cumulative_revenue_million.iloc[-1] > 0 else 'red'
        ax2.plot(cumulative_revenue_million.index, cumulative_revenue_million, color=color_line, lw=2)
        
        # Zone verte/rouge
        ax2.fill_between(cumulative_revenue_million.index, cumulative_revenue_million, 0, 
                         where=(cumulative_revenue_million > 0), color='green', alpha=0.1)
        ax2.fill_between(cumulative_revenue_million.index, cumulative_revenue_million, 0, 
                         where=(cumulative_revenue_million < 0), color='red', alpha=0.1)

        final_bilan = cumulative_revenue_million.iloc[-1]
        ax2.set_title(f"Bilan Financier Cumulé 2025 : {final_bilan:+.1f} Millions € (Estimé)", fontsize=16, fontweight='bold')
        ax2.set_ylabel("Gain Cumulé (Millions €)")
        
        plt.tight_layout()
        print(f"Graphe Coûts généré. Bilan final estimé : {final_bilan:.2f} M€")
        plt.show()