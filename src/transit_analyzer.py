import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class TransitAnalyzer:
    def __init__(self, df):
        self.df = df

    def plot_transit_vs_consumption(self):
        print("Analyse du rôle de Hub (Transit)...")
        
        # 1. Identification de la colonne Transit
        # Dans ton fichier, la colonne s'appelle simplement "Transit" (Colonne S / Index 18 environ)
        col_transit = next((c for c in self.df.columns if "Transit" == str(c).strip()), None)
        
        if not col_transit:
            # Recherche plus large si le nom exact change
            col_transit = next((c for c in self.df.columns if "Transit" in str(c)), None)
        
        if not col_transit:
            print("⚠️ Colonne 'Transit' introuvable dans le fichier.")
            print("Colonnes disponibles :", self.df.columns.tolist())
            return

        # 2. Préparation des données (kWh -> MW)
        # On crée un DF temporaire pour le calcul
        df_plot = pd.DataFrame(index=self.df.index)
        
        # Conversion kWh 15min -> MW moyen horaire
        df_plot['Transit_MW'] = self.df[col_transit].resample('h').sum() / 1000
        df_plot['Consumption_MW'] = self.df['Consumption_MW'] # Déjà calculé dans le loader en principe
        
        # Si 'Consumption_MW' n'est pas dans le DF (dépend de ton loader), on le recalcule :
        if 'Consumption_MW' not in self.df.columns:
             # On cherche la colonne consommation (souvent index 3 ou par nom)
             col_conso = next((c for c in self.df.columns if "verbrauchte" in str(c).lower() and "end" not in str(c).lower()), None)
             if col_conso:
                 df_plot['Consumption_MW'] = self.df[col_conso].resample('h').sum() / 1000

        # 3. Lissage (7 jours) pour la lisibilité
        df_smooth = df_plot.rolling(window=168, center=True).mean().dropna()

        # 4. Visualisation
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(14, 7))

        # Tracé de la Consommation (La référence)
        plt.plot(df_smooth.index, df_smooth['Consumption_MW'], 
                 label="Consommation Suisse (Besoin interne)", color='#c0392b', lw=2)

        # Tracé du Transit (Le Service rendu à l'Europe)
        plt.plot(df_smooth.index, df_smooth['Transit_MW'], 
                 label="Transit (Flux traversant)", color='#f1c40f', lw=2, linestyle='--')

        # Remplissage sous la courbe Transit pour montrer le volume
        plt.fill_between(df_smooth.index, df_smooth['Transit_MW'], color='#f1c40f', alpha=0.15)

        plt.title("La Suisse, Carrefour de l'Europe : Transit vs Consommation (2025)", fontsize=16, fontweight='bold')
        plt.ylabel("Puissance Moyenne (MW)")
        plt.legend()
        plt.tight_layout()
        
        # Annotation pour expliquer
        max_transit = df_smooth['Transit_MW'].max()
        plt.text(df_smooth.index[len(df_smooth)//2], max_transit, 
                 "Le réseau suisse transporte\ndes volumes énormes pour ses voisins", 
                 ha='center', va='bottom', fontsize=10, color='#f39c12', fontweight='bold',
                 bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

        print("Graphique Transit généré.")
        plt.show()