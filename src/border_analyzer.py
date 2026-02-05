import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class BorderAnalyzer:
    def __init__(self, df):
        self.df = df

    def plot_cross_border_flows(self):
        print("Analyse des flux transfrontaliers (Basé sur Loader)...")
        
        # 1. Sélection des colonnes déjà calculées par le Loader
        # On mappe les codes pays vers les noms d'affichage
        neighbors_map = {
            'Net_Flow_DE_MW': 'Allemagne (DE)',
            'Net_Flow_FR_MW': 'France (FR)',
            'Net_Flow_IT_MW': 'Italie (IT)',
            'Net_Flow_AT_MW': 'Autriche (AT)'
        }
        
        # On vérifie si les colonnes existent
        available_cols = [c for c in neighbors_map.keys() if c in self.df.columns]
        
        if not available_cols:
            print("❌ ERREUR : Pas de colonnes 'Net_Flow_XX_MW' trouvées. Vérifiez le Loader.")
            return

        # 2. Création du DF pour le graphique (On renrenomme les colonnes pour l'affichage)
        df_net_mw = self.df[available_cols].rename(columns=neighbors_map)

        # 3. Lissage 7 jours (Pour la lisibilité)
        df_smooth = df_net_mw.rolling(window=168, center=True).mean()
        
        # --- Visualisation ---
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(14, 8))

        colors = {
            'Allemagne (DE)': 'black', 
            'France (FR)': 'blue', 
            'Italie (IT)': 'green', 
            'Autriche (AT)': 'red'
        }
        
        # Plot des lignes
        for name in df_smooth.columns:
            ax.plot(df_smooth.index, df_smooth[name], label=name, color=colors.get(name, 'grey'), lw=1.5)

        # Ligne Zéro
        ax.axhline(0, color='black', linewidth=1, linestyle='--')
        
        # Annotations (Zone Export / Import)
        ax.text(0.98, 0.95, "EXPORT (Positif)\nLa Suisse VEND", transform=ax.transAxes, 
                fontsize=11, color='green', fontweight='bold', ha='right', va='top', 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
        
        ax.text(0.98, 0.05, "IMPORT (Négatif)\nLa Suisse ACHÈTE", transform=ax.transAxes, 
                fontsize=11, color='red', fontweight='bold', ha='right', va='bottom',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

        ax.set_title("Géopolitique Élec : Qui alimente la Suisse ? (Flux Nets Lissés 7j)", fontsize=16, fontweight='bold')
        ax.set_ylabel("Flux Net (MW) [+ Export / - Import]")
        
        ax.legend(loc='upper left', frameon=True)
        
        plt.tight_layout()
        plt.show()