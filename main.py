from src.generator import SwissGridGenerator
from src.analyzer import WinterGapAnalyzer
from src.visualizer import SwissGridVisualizer

def main():
    print("Démarrage de la simulation Swiss Winter Gap...")
    
    # 1. Génération des données simulées
    generator = SwissGridGenerator(year=2025)
    df = generator.generate_year_data()
    
    # 2. Analyse des flux (Calcul du déficit)
    analyzer = WinterGapAnalyzer(df)
    df_analyzed = analyzer.analyze()
    
    # 3. Visualisation graphique
    visualizer = SwissGridVisualizer(df_analyzed)
    visualizer.plot_winter_gap()

if __name__ == "__main__":
    main()