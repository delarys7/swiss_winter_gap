import matplotlib.pyplot as plt
import seaborn as sns

class SwissGridVisualizer:
    def __init__(self, df):
        self.df = df
        # On définit le style général une bonne fois pour toutes
        sns.set_theme(style="whitegrid")

    def plot_raw_data(self):
        """
        MODE BRUT : Affiche chaque heure (8760 points).
        Utile pour voir la volatilité, les pics extrêmes et le "bruit" du marché.
        """
        plt.figure(figsize=(14, 7))
        
        # Tracé fin (linewidth=0.5) car il y a beaucoup de points
        plt.plot(self.df.index, self.df['Consumption_MW'], label='Conso (Brute)', color='#c0392b', lw=0.5, alpha=0.8)
        plt.plot(self.df.index, self.df['Production_MW'], label='Prod (Brute)', color='#27ae60', lw=0.5, alpha=0.8)

        plt.title("Vue Technique : Volatilité Horaire du Réseau Suisse (2025)", fontsize=14, fontweight='bold')
        plt.ylabel("Puissance (MW)")
        plt.xlabel("Date")
        plt.legend(loc='upper right')
        plt.tight_layout()
        
        print("Graphe BRUT généré (ferme la fenêtre pour voir le suivant).")
        plt.show()

    def plot_smoothed_trend(self):
        """
        MODE LISSÉ : Moyenne mobile sur 7 jours (168h).
        Utile pour voir le 'Winter Gap', les tendances saisonnières et les déficits structurels.
        """
        # Calcul de la moyenne glissante (Rolling Mean)
        # window=168 : On prend 168h (7 jours)
        # center=True : On place le point au milieu de la semaine (pour ne pas décaler la courbe visuellement)
        df_smooth = self.df.rolling(window=168, center=True).mean()

        plt.figure(figsize=(14, 7))

        # Tracé plus épais (linewidth=2) car c'est une tendance
        plt.plot(df_smooth.index, df_smooth['Consumption_MW'], label='Conso (Moyenne 7j)', color='#c0392b', lw=2)
        plt.plot(df_smooth.index, df_smooth['Production_MW'], label='Prod (Moyenne 7j)', color='#27ae60', lw=2)

        # Remplissage des zones (Gap vs Surplus)
        plt.fill_between(df_smooth.index, 
                         df_smooth['Consumption_MW'], 
                         df_smooth['Production_MW'], 
                         where=(df_smooth['Consumption_MW'] > df_smooth['Production_MW']),
                         color='#c0392b', alpha=0.2, label='Déficit (Winter Gap)')

        plt.fill_between(df_smooth.index, 
                         df_smooth['Consumption_MW'], 
                         df_smooth['Production_MW'], 
                         where=(df_smooth['Production_MW'] > df_smooth['Consumption_MW']),
                         color='#27ae60', alpha=0.2, label='Surplus (Summer Export)')

        plt.title("Vue Stratégique : Le 'Winter Gap' Suisse (Lissé 7 jours)", fontsize=16, fontweight='bold')
        plt.ylabel("Puissance Moyenne (MW)")
        plt.ylim(bottom=0) # On part de 0 pour l'échelle
        plt.legend(loc='upper right')
        plt.tight_layout()
        
        print("Graphe LISSÉ généré.")
        plt.show()