import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class AdvancedAnalyzer:
    def __init__(self, df):
        self.df = df
        sns.set_theme(style="whitegrid")

    def plot_duration_curve(self):
        """
        ÉTUDE 1 : Monotone de Charge Résiduelle (RLDC)
        Trie les heures par déficit décroissant.
        """
        print("Génération Monotone de Charge Résiduelle...")
        
        # Calcul du Gap (>0 si on doit importer)
        gap = (self.df['Consumption_MW'] - self.df['Production_MW'])
        
        # On trie du plus grand déficit au plus grand surplus
        gap_sorted = gap.sort_values(ascending=False).reset_index(drop=True)
        
        plt.figure(figsize=(12, 6))
        
        # Zone Déficit (Besoin d'import)
        plt.fill_between(gap_sorted.index, gap_sorted, 0, 
                         where=(gap_sorted > 0), color='#e74c3c', alpha=0.3, label='Déficit (Besoin Import)')
        
        # Zone Surplus (Capacité Export)
        plt.fill_between(gap_sorted.index, gap_sorted, 0, 
                         where=(gap_sorted < 0), color='#2ecc71', alpha=0.3, label='Surplus (Export Possible)')
        
        plt.plot(gap_sorted.index, gap_sorted, color='black', lw=2)
        
        # Ligne zéro
        plt.axhline(0, color='black', linestyle='--')
        
        plt.title("Monotone de Charge Résiduelle (Residual Load Duration Curve)", fontsize=14, fontweight='bold')
        plt.xlabel("Heures cumulées (0 à 8760)")
        plt.ylabel("Déficit / Surplus (MW)")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_seasonal_heatmap(self):
        """
        ÉTUDE 2 : Heatmap Saisonnier (Mois vs Heure)
        Visualise quand le déficit frappe le plus fort.
        """
        print("Génération Heatmap Saisonnier...")
        
        df_hm = self.df.copy()
        df_hm['Month'] = df_hm.index.month
        df_hm['Hour'] = df_hm.index.hour
        
        # On calcule le Gap moyen pour chaque couple (Mois, Heure)
        # Gap positif = Déficit (Rouge), Gap négatif = Surplus (Bleu)
        df_hm['Gap'] = df_hm['Consumption_MW'] - df_hm['Production_MW']
        
        pivot_table = df_hm.pivot_table(values='Gap', index='Hour', columns='Month', aggfunc='mean')
        
        plt.figure(figsize=(10, 8))
        
        # Palette : Rouge (Déficit) -> Blanc (Équilibre) -> Bleu/Vert (Surplus)
        # On inverse souvent : Rouge = Danger (Déficit). Ici RdBu_r (Red-Blue reversed)
        sns.heatmap(pivot_table, cmap='RdBu_r', center=0, annot=False, cbar_kws={'label': 'Déficit Moyen (MW)'})
        
        plt.title("Signature Temporelle du Winter Gap (Moyenne Mensuelle)", fontsize=14, fontweight='bold')
        plt.xlabel("Mois")
        plt.ylabel("Heure de la journée")
        plt.gca().invert_yaxis() # 0h en bas, 23h en haut
        plt.tight_layout()
        plt.show()

    def plot_price_correlation(self):
        """
        ÉTUDE 3 : Scatter Plot (Position Nette vs Prix Proxy)
        """
        print("Génération Corrélation Prix vs Volume...")
        
        # On recalcule les colonnes nécessaires si pas dispo
        # On cherche les colonnes Prix
        col_price_pos = next((c for c in self.df.columns if "positive" in str(c).lower() and "preise" in str(c).lower()), None)
        col_price_neg = next((c for c in self.df.columns if "negative" in str(c).lower() and "preise" in str(c).lower()), None)
        
        if not col_price_pos:
            print("⚠️ Pas de prix trouvé pour le Scatter Plot.")
            return

        # Prix Proxy
        avg_price = (self.df[col_price_pos] + self.df[col_price_neg]) / 2
        
        # Net Position (Export - Import)
        # Attention : Dans analyzer.py on avait calculé Net_Position_MW, sinon on le refait
        net_pos = self.df['Production_MW'] - self.df['Consumption_MW']
        
        plt.figure(figsize=(10, 6))
        
        # Scatter plot avec transparence pour voir la densité
        sc = plt.scatter(net_pos, avg_price, c=avg_price, cmap='viridis', alpha=0.3, s=10)
        
        plt.axvline(0, color='black', linestyle='--', lw=1)
        plt.colorbar(sc, label='Prix Proxy (€/MWh)')
        
        plt.title("Corrélation : Position Commerciale vs Prix", fontsize=14, fontweight='bold')
        plt.xlabel("Position Nette (MW) \n < 0 : Import (Achat) | > 0 : Export (Vente)")
        plt.ylabel("Prix Proxy (€/MWh)")
        
        # Annotations des zones
        plt.text(net_pos.min()*0.8, avg_price.max()*0.9, "Zone Critique :\nAchats chers", color='red', fontweight='bold')
        plt.text(net_pos.max()*0.6, avg_price.min()*1.1, "Zone Rentable :\nVente bas prix?", color='green', fontweight='bold')

        plt.tight_layout()
        plt.show()