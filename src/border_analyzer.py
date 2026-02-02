import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class BorderAnalyzer:
    def __init__(self, df):
        self.df = df

    def plot_cross_border_flows(self):
        print("Analyse des flux transfrontaliers...")
        
        neighbors = {
            'DE': 'Allemagne (DE)', 
            'FR': 'France (FR)', 
            'IT': 'Italie (IT)', 
            'AT': 'Autriche (AT)'
        }
        
        df_net_mw = pd.DataFrame(index=self.df.index)

        # Recherche des colonnes (Export - Import)
        for code, name in neighbors.items():
            col_export = next((c for c in self.df.columns if f"CH->{code}" in str(c)), None)
            col_import = next((c for c in self.df.columns if f"{code}->CH" in str(c)), None)
            
            if col_export and col_import:
                # Calcul Net (MW)
                net_kwh = self.df[col_export] - self.df[col_import]
                df_net_mw[name] = net_kwh.resample('h').sum() / 1000

        if df_net_mw.empty:
            print("❌ ERREUR : Pas de données frontières.")
            return

        # Lissage 7 jours
        df_smooth = df_net_mw.rolling(window=168, center=True).mean()
        
        # --- Visualisation ---
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(14, 8)) # On crée l'objet 'ax' pour mieux contrôler

        colors = {'Allemagne (DE)': 'black', 'France (FR)': 'blue', 'Italie (IT)': 'green', 'Autriche (AT)': 'red'}
        
        for name in df_smooth.columns:
            ax.plot(df_smooth.index, df_smooth[name], label=name, color=colors.get(name, 'grey'), lw=1.5)

        # Ligne Zéro
        ax.axhline(0, color='black', linewidth=1, linestyle='--')
        
        # Annotations (Positionnées intelligemment via 'transAxes')
        # (0.98, 0.95) = Coin Haut Droit
        ax.text(0.98, 0.95, "EXPORT (Positif)\nLa Suisse VEND", transform=ax.transAxes, 
                fontsize=11, color='green', fontweight='bold', ha='right', va='top', 
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
        
        # (0.98, 0.05) = Coin Bas Droit
        ax.text(0.98, 0.05, "IMPORT (Négatif)\nLa Suisse ACHÈTE", transform=ax.transAxes, 
                fontsize=11, color='red', fontweight='bold', ha='right', va='bottom',
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

        ax.set_title("Géopolitique Élec : Qui alimente la Suisse ? (Flux Nets Lissés 7j)", fontsize=16, fontweight='bold')
        ax.set_ylabel("Flux Net (MW) [+ Export / - Import]")
        
        # Légende en haut à gauche (loc='upper left')
        ax.legend(loc='upper left', frameon=True)
        
        plt.tight_layout()
        print("Graphique Flux Frontaliers généré.")
        plt.show()