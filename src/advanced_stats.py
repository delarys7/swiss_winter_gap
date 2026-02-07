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
        Basé sur la colonne 'Residual_Load_MW' calculée par le Loader.
        """
        print("Génération Monotone de Charge Résiduelle (RLDC)...")
        
        if 'Residual_Load_MW' not in self.df.columns:
            print("⚠️ Erreur: 'Residual_Load_MW' manquante.")
            return
        
        # Tri décroissant (Du plus gros Déficit au plus gros Surplus)
        gap_sorted = self.df['Residual_Load_MW'].sort_values(ascending=False).reset_index(drop=True)
        
        plt.figure(figsize=(12, 6))
        
        # Zone Déficit (Besoin d'import) : Valeurs > 0
        plt.fill_between(gap_sorted.index, gap_sorted, 0, 
                         where=(gap_sorted > 0), color='#e74c3c', alpha=0.3, label='Déficit (Import Requis)')
        
        # Zone Surplus (Capacité Export) : Valeurs < 0
        plt.fill_between(gap_sorted.index, gap_sorted, 0, 
                         where=(gap_sorted < 0), color='#2ecc71', alpha=0.3, label='Surplus (Export Possible)')
        
        plt.plot(gap_sorted.index, gap_sorted, color='black', lw=1.5)
        
        # Ligne zéro
        plt.axhline(0, color='black', linestyle='--')
        
        plt.title("Monotone de Charge Résiduelle (Residual Load Duration Curve)", fontsize=14, fontweight='bold')
        plt.xlabel("Heures cumulées (0 à 8760)")
        plt.ylabel("Déficit (+) / Surplus (-) [MW]")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_seasonal_heatmap(self):
        """
        ÉTUDE 2 : Heatmap Saisonnier (Mois vs Heure)
        Utilise 'Residual_Load_MW' pour colorer les zones de tension.
        """
        print("Génération Heatmap Saisonnier...")
        
        if 'Residual_Load_MW' not in self.df.columns: return
        
        # Préparation des données pivot
        df_hm = self.df[['Residual_Load_MW']].copy()
        df_hm['Month'] = df_hm.index.month
        df_hm['Hour'] = df_hm.index.hour
        
        # Pivot : Lignes=Heures, Colonnes=Mois, Valeur=Gap Moyen
        pivot_table = df_hm.pivot_table(values='Residual_Load_MW', index='Hour', columns='Month', aggfunc='mean')
        
        plt.figure(figsize=(10, 8))
        
        # Palette : Rouge (Déficit > 0) -> Blanc (0) -> Bleu (Surplus < 0)
        # 'RdBu_r' met le Rouge pour les valeurs positives (Déficit) et Bleu pour négatives (Surplus)
        sns.heatmap(pivot_table, cmap='RdBu_r', center=0, annot=False, 
                    cbar_kws={'label': 'Gap Moyen (MW) [Rouge=Déficit]'})
        
        plt.title("Signature Temporelle du Winter Gap (Moyenne Mensuelle)", fontsize=14, fontweight='bold')
        plt.xlabel("Mois")
        plt.ylabel("Heure de la journée")
        plt.gca().invert_yaxis() # 0h en bas
        
        plt.tight_layout()
        plt.show()

    def plot_price_correlation(self):
        """
        ÉTUDE 3 : Scatter Plot (Position Nette vs Prix Proxy)
        Utilise 'Price_EUR' calculé par le Loader.
        """
        print("Génération Corrélation Prix vs Volume...")
        
        if 'Price_EUR' not in self.df.columns or 'Residual_Load_MW' not in self.df.columns:
            print("⚠️ Données manquantes pour la corrélation.")
            return

        # Position Commerciale = Production - Consommation = -Residual_Load
        # Si Residual_Load > 0 (Déficit), alors Position < 0 (Import)
        net_position = -self.df['Residual_Load_MW']
        prices = self.df['Price_EUR']
        
        plt.figure(figsize=(10, 6))
        
        # Scatter plot
        sc = plt.scatter(net_position, prices, c=prices, cmap='viridis', alpha=0.3, s=10)
        
        plt.axvline(0, color='black', linestyle='--', lw=1)
        plt.colorbar(sc, label='Prix Proxy (€/MWh)')
        
        plt.title("Corrélation : Position Commerciale vs Prix", fontsize=14, fontweight='bold')
        plt.xlabel("Position Nette (MW) \n < 0 : Import (Achat) | > 0 : Export (Vente)")
        plt.ylabel("Prix Proxy (€/MWh)")
        
        # Annotations simples
        plt.text(net_position.min()*0.9, prices.max()*0.9, "IMPORT\n(Prix Hauts)", color='red', fontweight='bold', ha='left')
        plt.text(net_position.max()*0.9, prices.min()*1.1, "EXPORT\n(Prix Bas)", color='green', fontweight='bold', ha='right')

        plt.tight_layout()
        plt.show()