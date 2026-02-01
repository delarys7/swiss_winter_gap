from src.loader import SwissGridLoader
from src.analyzer import WinterGapAnalyzer
from src.visualizer import SwissGridVisualizer
from src.border_analyzer import BorderAnalyzer
import os

def main():
    print("Démarrage Swiss Winter Gap & Border Analysis...")
    
    file_name = 'swissgrid_2025.xlsx'
    file_path = os.path.join('data', file_name)
    
    loader = SwissGridLoader(file_path)
    df = loader.load_data()
    
    if df is not None:
        # 1. Analyse Winter Gap
        analyzer = WinterGapAnalyzer(df)
        df_analyzed = analyzer.analyze()
        
        visualizer = SwissGridVisualizer(df_analyzed)
        
        # --- A. Vue Brute (Technique) ---
        # Affiche le bruit, les pics horaires, la réalité physique 15min/1h
        visualizer.plot_raw_data()
        
        # --- B. Vue Lissée (Stratégique) ---
        # Affiche la tendance lourde (Winter Gap)
        visualizer.plot_smoothed_trend()
        
        # 2. Analyse des Frontières
        border = BorderAnalyzer(df)
        border.plot_cross_border_flows()
        
    else:
        print("❌ Problème de chargement.")

if __name__ == "__main__":
    main()