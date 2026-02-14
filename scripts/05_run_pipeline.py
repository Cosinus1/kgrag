# scripts/05_run_pipeline.py

import sys
sys.path.append('.')

import subprocess
from pathlib import Path

def run_script(script_name):
    """Exécute un script Python."""
    print(f"\n{'='*60}")
    print(f"Exécution de {script_name}")
    print('='*60)
    
    try:
        # Use utf-8 encoding for subprocess
        result = subprocess.run(
            ['python', script_name], 
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur lors de l'exécution de {script_name}")
        print(f"Code de retour: {e.returncode}")
        return False
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        return False

def main():
    print("="*60)
    print("PIPELINE COMPLET - Knowledge Graph RAG")
    print("="*60)
    
    # Vérifier que les répertoires de base existent
    data_raw = Path("data/raw")
    if not data_raw.exists():
        print(f"\n❌ Le répertoire {data_raw} n'existe pas!")
        print("\nVeuillez d'abord télécharger les données:")
        print("  python scripts/00_load_data.py")
        return
    
    # Compter les fichiers
    txt_files = list(data_raw.glob("*.txt"))
    if len(txt_files) == 0:
        print(f"\n❌ Aucun fichier trouvé dans {data_raw}!")
        print("\nVeuillez d'abord télécharger les données:")
        print("  python scripts/00_load_data.py")
        return
    
    print(f"\n✓ Trouvé {len(txt_files)} fichiers dans data/raw/")
    
    # Scripts à exécuter
    scripts = [
        ('01_prepare_corpus.py', 'Préparation du corpus'),
        ('02_extract_entities.py', 'Extraction des entités et relations'),
        ('03_build_graph.py', 'Construction du graphe Neo4j'),
        ('04_generate_embeddings.py', 'Génération des embeddings')
    ]
    
    print(f"\n📋 Pipeline à exécuter:")
    for i, (script, desc) in enumerate(scripts, 1):
        print(f"  {i}. {desc} ({script})")
    
    response = input("\n▶️  Lancer le pipeline complet? (y/n, défaut=y): ").strip().lower()
    if response == 'n':
        print("Pipeline annulé.")
        return
    
    print("\n🚀 Démarrage du pipeline...\n")
    
    # Exécuter chaque script
    for i, (script, desc) in enumerate(scripts, 1):
        script_path = f'scripts/{script}'
        
        print(f"\n{'#'*60}")
        print(f"# ÉTAPE {i}/{len(scripts)}: {desc}")
        print(f"{'#'*60}")
        
        if not run_script(script_path):
            print(f"\n❌ ÉCHEC à l'étape {i}/{len(scripts)}")
            print(f"Script: {script}")
            print(f"\nLe pipeline s'est arrêté. Corrigez l'erreur et relancez.")
            return
        
        print(f"\n✓ Étape {i}/{len(scripts)} terminée avec succès")
    
    # Résumé final
    print(f"\n{'='*60}")
    print("PIPELINE TERMINÉ AVEC SUCCÈS! 🎉")
    print("="*60)
    
    # Vérifier que tout est bien créé
    files_created = {
        "Documents traités": Path("data/processed/documents.json"),
        "Entités extraites": Path("data/entities/entities.json"),
        "Relations extraites": Path("data/relations/relations.json"),
        "Vector store": Path("chroma_db")
    }
    
    print("\n📁 Fichiers créés:")
    all_good = True
    for name, filepath in files_created.items():
        if filepath.exists():
            if filepath.is_file():
                size = filepath.stat().st_size / 1024 / 1024  # MB
                print(f"  ✓ {name}: {filepath} ({size:.2f} MB)")
            else:
                print(f"  ✓ {name}: {filepath}")
        else:
            print(f"  ✗ {name}: {filepath} (manquant)")
            all_good = False
    
    if all_good:
        print("\n🎉 Tout est prêt!")
    else:
        print("\n⚠️  Certains fichiers sont manquants")
    
    print(f"\n{'='*60}")
    print("PROCHAINES ÉTAPES")
    print("="*60)
    print("\n1. Lancer l'interface Streamlit:")
    print("   streamlit run app/streamlit_app.py")
    print("\n2. Ou lancer l'API FastAPI:")
    print("   python app/api.py")
    print("\n3. Tester une requête:")
    print('   curl -X POST http://localhost:8000/ask \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"question": "Qui est Napoleon?"}\'')
    print("\n" + "="*60)

if __name__ == "__main__":
    main()