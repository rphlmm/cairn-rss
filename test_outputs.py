# python cairn_scraper3.py --formats txt json csv atom
# python test_outputs.py

def test_outputs():
    # Chemin de base
    output_dir = Path("output/data")
    
    # Lire et vérifier le fichier JSON
    # json_files = list(output_dir.glob("*.json"))
    # latest_json = max(json_files, key=lambda x: x.stat().st_mtime)
    # with open(latest_json) as f:
    #     json_data = json.load(f)
    #     print(f"JSON: {len(json_data)} publications")
    #     print(json_data[0])  # Affiche la première publication

    # Lire et vérifier le fichier CSV 
    # csv_files = list(output_dir.glob("*.csv"))
    # latest_csv = max(csv_files, key=lambda x: x.stat().st_mtime)
    # with open(latest_csv) as f:
    #     csv_reader = csv.DictReader(f)
    #     data = list(csv_reader)
    #     print(f"\nCSV: {len(data)} publications")
    #     print(data[0])

    # Lire et vérifier le fichier TXT
    txt_files = list(output_dir.glob("*.txt"))
    latest_txt = max(txt_files, key=lambda x: x.stat().st_mtime)
    with open(latest_txt) as f:
        print(f"\nTXT contenu:")
        print(f.read()[:500] + "...")  # Affiche le début du fichier

    # Lire et vérifier le flux Atom
    atom_file = output_dir / "cairn_feed.atom"
    with open(atom_file) as f:
        atom_content = f.read()
        print(f"\nAtom flux:")
        print(atom_content[:500] + "...")  # Affiche le début du flux

if __name__ == "__main__":
    test_outputs()