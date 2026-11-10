# Générateur de cas de test Gherkin avec un LLM local (Ollama)

Framework Python qui lit des spécifications (`.yaml`, `.docx`, `.pdf`, `.xlsx`), les découpe en **exigences**, complète un
**dictionnaire de steps**, puis génère **un fichier `.feature` par exigence** avec un LLM local (Ollama).

## Démarche d'exécution

```
specs/*.{yaml,yml,docx,pdf,xlsx}
      │
      ▼  1. exigence_prompt.txt   (+ catalogue unique mapping/modules.yaml)
 exigences (JSON)  ──►  scenarios/client/<spec>_<modèle>/exigences.json
      │
      ▼  2. dictionary_prompt.txt (+ dictionnaire existant dictionary/steps.yaml ; module de chaque exigence)
 phrases manquantes ──►  ajoutées à la fin de dictionary/steps.yaml
      │
      ▼  3. gherkin_prompt.txt    (1 appel par exigence : exigence + spécification + dictionnaire)
 scenarios/client/<spec>_<modèle>/SPEC-SUP-001.feature, SPEC-INV-001.feature ...
```

Chaque fichier `.feature` reçoit ses tags (ajoutés par le code, pas par le LLM) :

```gherkin
@id:SC-SUP-001 @module:Supplier_Info_Management @exigence:SPEC-SUP-001
Feature: Référencement d'un nouveau fournisseur

  Scenario: Un acheteur référence un fournisseur avec un SIRET valide
    Given je suis connecté en tant que "Acheteur"
    ...
```

| Tag | Valeur |
|---|---|
| `@id:SC-SUP-001` | identifiant du scénario : celui de l'exigence avec le préfixe `SC-` à la place de `SPEC-` |
| `@module:Supplier_Info_Management` | libellé du module (`Label (EN)` de `mapping/modules.yaml`, espaces remplacés par `_`) |
| `@exigence:SPEC-SUP-001` | code de l'exigence dont le scénario est issu |

## Structure

```
gherkin_framework/
├── main.py                       # point d'entrée (CLI)
├── config.yaml                   # modèle LLM, paramètres, chemins
├── requirements.txt
├── packages/
│   └── scenario-generator/
│       ├── exigence_prompt.txt       # spécification -> exigences (JSON). Marqueur : {speccode}
│       ├── dictionary_prompt.txt     # exigences -> steps manquants (JSON). Marqueur : __MAX_STEPS__
│       └── gherkin_prompt.txt        # exigence -> Feature. Marqueurs : {exigence} {spec} {steps} {gherkin_language}
├── dictionary/
│   └── steps.yaml                # dictionnaire de steps (complété automatiquement, jamais réécrit)
├── mapping/
│   └── modules.yaml              # catalogue unique : Functional Module, Technical module, Label (EN)
├── specs/                        # spécifications .yaml/.yml/.docx/.pdf/.xlsx (sous-dossiers acceptés)
├── scenarios/
│   └── client/                   # un dossier par spécification et par modèle
├── logs/                         # execution.log
└── src/
    ├── config.py                 # lecture de config.yaml
    ├── specs.py                  # lecture des spécifications YAML
    ├── prompts.py                # remplissage des prompts, lecture du JSON du LLM
    ├── llm.py                    # appel Ollama + mesures + ligne Excel (un appel = une ligne)
    ├── mapping.py                # lecture du catalogue unique des modules
    ├── exigences.py              # étape 1 : validation des exigences et codes de module
    ├── dictionary.py             # étape 2 : dictionnaire de steps
    ├── generator.py              # étape 3 + orchestration + tags
    ├── hardware.py, report.py, logging_setup.py
```

## Catalogue des modules

`mapping/modules.yaml` est l'unique catalogue utilisé pour classer les exigences. Chaque entrée contient
`Functional Module` (le code), `Technical module` et `Label (EN)` ; `Technical module: null` est accepté.
Il est exploité à l'étape 1 :

- `exigence_prompt.txt` : le catalogue (par exemple `inv = Invoices [E-procurement]`) est fourni au LLM, qui renvoie
  `moduleCode`. Le code valide ce code dans le catalogue et ajoute lui-même le libellé et le module technique.
- `dictionary_prompt.txt` : le module associé à chaque exigence est ajouté à la description fonctionnelle comme
  contexte de vocabulaire.

Le code `Functional Module` pilote les identifiants `SPEC-<MODULE>-<NNN>` et le libellé pilote le tag `@module`.
Le fichier se règle avec `paths.modules_file` dans `config.yaml`.

## Format d'une spécification

```yaml
code: SPEC-FRN-001          # identifiant de la spécification, devient {speccode} et specCode
titre: Gestion du cycle fournisseur dans Ivalua   # facultatif
contenu: |                  # obligatoire
  Texte de la spécification...
```

Pour une spécification YAML, fournir `code` et `contenu` comme dans l'exemple ci-dessus. Pour un fichier DOCX,
PDF ou XLSX, le texte du document est extrait automatiquement et son code est dérivé du nom de fichier
(par exemple `fournisseurs_v2.docx` devient `SPEC-FOURNISSEURS-V2`). Dans un DOCX, les paragraphes et tableaux
sont lus ; les PDF doivent contenir du texte sélectionnable (les PDF numérisés nécessitent un OCR préalable) ;
dans un XLSX, les cellules non vides de toutes les feuilles sont lues. Déposer le fichier dans `specs/`
ou le passer explicitement en argument. Si la spécification introduit un nouveau domaine, ajouter son module
dans `mapping/modules.yaml`.

## Installation

1. Installer [Ollama](https://ollama.com) et démarrer le serveur, puis `ollama pull qwen3:14b`.
2. `pip install -r requirements.txt` (Python 3.9 ou plus ; inclut les lecteurs DOCX/PDF).

## Utilisation

```bash
python main.py                                    # toutes les spécifications de specs/
python main.py specs/client/fournisseurs.yaml     # une seule spécification
python main.py specs/client/specification.docx    # DOCX, PDF ou XLSX également acceptés
python main.py --model ministral-3:8b             # change de modèle sans modifier config.yaml
python main.py --language fr                      # mots-clés Gherkin en français
```

Code de sortie : `0` succès, `1` au moins un échec, `2` erreur de configuration ou aucune spécification,
`130` si l'exécution est interrompue avec `Ctrl+C`. L'appel au LLM en cours est arrêté, marqué
`INTERRUPTED` dans le rapport, puis le programme affiche son récapitulatif avant de quitter.

## Sorties

- `scenarios/client/<spec>_<modèle>/exigences.json` : exigences au format `exigenceCode / libelle / specCode / statusCode / moduleCode`.
  Les codes `SPEC-<MODULE>-<NNN>` sont recalculés par le code (séquentiels par module, à partir de 001) et les
  exigences dont le module n'est pas dans `mapping/modules.yaml` sont écartées.
- `scenarios/client/<spec>_<modèle>/<exigenceCode>.feature` : un fichier par exigence. Une réponse qui ne contient pas
  de scénario n'est pas enregistrée : l'exigence est comptée en échec (statut `FAILED` dans l'Excel).
- `dictionary/steps.yaml` : les phrases nouvelles sont ajoutées à la fin ; celles qui existent déjà (même phrase,
  quels que soient les noms de paramètres), qui commencent par un mot-clé Gherkin ou par « je sais que » sont écartées.
- `scenarios/client/executions.xlsx` : **une ligne par appel au LLM** (colonne `Step` : exigences / dictionary / gherkin, colonne
  `Exigence`). Si un ancien fichier au format précédent existe, il est renommé `executions_old_<date>.xlsx`.

## Réglages

`config.yaml` : modèle, `temperature`, `num_ctx` (16384 : le prompt Gherkin contient la spécification et tout le
dictionnaire), `think`, `generation.max_steps` (nouvelles phrases max par spécification) et tous les chemins.
Un avertissement est écrit dans les logs si prompt + réponse atteignent `num_ctx` (entrée tronquée possible).

## Performances (CPU) et récapitulatif final

- **Tableau récapitulatif** : affiché une seule fois, à la fin de l'exécution, après la génération de tous les
  `.feature` (une ligne par appel au LLM + une ligne TOTAL, puis la liste des fichiers générés). Il s'affiche aussi
  si l'exécution est interrompue (Ctrl+C). `scenarios/client/executions.xlsx` reste complété après chaque appel.
- **Cache de préfixe Ollama** : dans `gherkin_prompt.txt`, la spécification et le dictionnaire sont placés AVANT
  l'exigence. Le début du prompt est identique d'une exigence à l'autre : Ollama ne le retraite pas.
- **Dictionnaire filtré** : seules les `generation.max_dictionary_steps` phrases les plus proches de la spécification
  sont envoyées au LLM (`steps.yaml` n'est jamais réduit ; les phrases « je sais que » ne sont pas envoyées).
- **Plafonds de tokens par étape** (`llm.num_predict_*`) : une réponse coupée est récupérée (éléments complets
  conservés) au lieu de bloquer l'exécution. `generation.max_exigences` limite le nombre d'appels Gherkin.
- Le prompt « exigences » ne demande que `libelle` et `moduleCode` (le code ajoute les métadonnées du module).
- `gherkin_prompt.txt` au format JSON (`scenarios`/`steps`) est converti en `.feature` (un fichier par exigence,
  `generation.max_scenarios` scénarios maximum) ; les `new_phrase` sont ajoutées à `steps.yaml`. L'ancien format
  (texte Gherkin) reste accepté.

## Limites

- Le Gherkin généré est un point de départ : il doit être relu par un humain (hypothèses marquées `# ASSUMPTION:`).
- Un fichier de sortie existant du même nom est écrasé.
- Le nombre d'appels au LLM est de `2 + nombre d'exigences` par spécification : prévoir du temps sur CPU.
