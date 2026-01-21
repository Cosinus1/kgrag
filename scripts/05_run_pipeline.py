# scripts/05_run_pipeline.py

import sys
sys.path.append('.')

import subprocess

def run_script(script_name):
    """Exécute un script Python."""
    print(f"\n{'='*60}")
    print(f"Exécution de {script_name}")
    print('='*60)
    result = subprocess.run(['python', script_name], check=True)
    return result.returncode == 0

def main():
    scripts = [
        'scripts/01_prepare_corpus.py',
        'scripts/02_extract_entities.py',
        'scripts/03_build_graph.py',
        'scripts/04_generate_embeddings.py'
    ]
    
    print("Démarrage du pipeline complet...")
    
    for script in scripts:
        if not run_script(script):
            print(f"Erreur lors de l'exécution de {script}")
            return
    
    print("\n" + "="*60)
    print("Pipeline terminé avec succès!")
    print("="*60)
    print("\nVous pouvez maintenant lancer l'application:")
    print("  streamlit run app/streamlit_app.py")

if __name__ == "__main__":
    main()
