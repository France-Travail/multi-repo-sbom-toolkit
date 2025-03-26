# 🧰 Scripts `multi-repo-sbom-individual.py` et `multi-repo-sbom-global.py`

## 📌 Objectif

Automatiser la génération de SBOMs (Software Bill of Materials) pour plusieurs dépôts Git en utilisant **OSS Review Toolkit (ORT)** et **ScanCode Toolkit**. Ces scripts sont conçus pour les besoins d’une OSPO ou d’un audit logiciel couvrant plusieurs composants répartis en différents dépôts.

### 🧭 Ordre d'exécution recommandé

1. \*\*Étape 1 : \*\***`multi-repo-sbom-individual.py`** → analyse indépendante de chaque projet.
2. \*\*Étape 2 : \*\***`multi-repo-sbom-global.py`** → analyse consolidée de tous les projets dans un seul répertoire.

Cela permet d’avoir à la fois une vue fine par composant, et une vue d’ensemble du projet globale.

---

## ⚙️ Fonctionnalités principales (individuel + global)

- Clonage automatique de plusieurs dépôts Git à partir d’un fichier JSON.
- Analyse des dépendances avec `ort analyze`.
- Génération du SBOM au format `EvaluatedModel` via `ort report`.
- Intégration d’une analyse complémentaire via **ScanCode Toolkit**.
- Comptage automatique du nombre de dépendances (version individuelle).
- Résumé global dans `summary.csv`.
- Journalisation des erreurs dans `error_log.txt` ou `error_log_global.txt`.
- Option `--skip-existing` (individuel) pour éviter les doublons.

---

## 📁 Structure attendue

Les scripts utilisent un fichier `repos.json` pour connaître la liste des dépôts à analyser.

📌 **Ce fichier doit être placé à la racine du dossier contenant les scripts**, et **doit s’appeler exactement `repos.json`** (sauf modification du script).


### Exemple de fichier `repos.json`

```json
[
  {
    "name": "design-button",
    "url": "https://github.com/ton-org/design-button"
  },
  { "name": "design-card", "url": "https://github.com/ton-org/design-card" }
]
```

---

## 🚀 Utilisation

### Étape 1 : Analyse par projet

```bash
python3 multi-repo-sbom-individual.py
```

Ou pour ignorer les projets déjà traités:

```bash
python3 multi-repo-sbom-individual.py --skip-existing
```

### Étape 2 : Analyse consolidée

```bash
python3 multi-repo-sbom-global.py
```

---

## 🗂️ Résultats générés

### Par projet (via `multi-repo-sbom-individual.py`)

```
sboms/
└── design-button/
    ├── analyzer-result.yml
    ├── evaluatedModel.json
    └── scancode_results.json
```

### Résumé CSV

- `sboms/summary.csv` : Tableau `projet | nombre de dépendances`

### Analyse globale (via `multi-repo-sbom-global.py`)

```
sboms/_global/
├── analyzer-result.yml
├── evaluatedModel.json
└── scancode_results.json
```

---

## 🔎 Dépendances requises

- [OSS Review Toolkit (ORT)](https://github.com/oss-review-toolkit/ort) installé et accessible via `ort`

- Python ≥ 3

- ORT (OSS Review Toolkit) installé et accessible via `ort`

- [ScanCode Toolkit](https://github.com/nexB/scancode-toolkit) installé via `scancode`

- Git installé et accessible

---

## 🛠️ Personnalisation possible

- Gestion de branches/tags spécifiques
- Ajout d’un export au format CycloneDX ou SPDX (`-f CycloneDx`)
- Conteneurisation des outils avec Docker

---

## 📞 Contact / Support

Ces scripts peuvent être intégrés dans un pipeline CI/CD, dans un processus d’audit, ou pour une gouvernance open source à l’échelle d’une organisation.

Pour toute amélioration, automatisation ou conteneurisation, contacter l’équipe OSPO.

