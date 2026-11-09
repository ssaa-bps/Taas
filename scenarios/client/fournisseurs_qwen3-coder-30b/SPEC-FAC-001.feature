@id:SC-FAC-001 @module:Factures @exigence:SPEC-FAC-001
Feature: Importation et traitement des factures fournisseurs

  Scenario: Importation d'une facture valide
    Given je suis sur la page "Importation des factures"
    When je tente d'importer une facture avec les champs suivants : identifiant fournisseur 'SUPP001', numéro de facture 'INV-2023-001', date de facture '2023-10-15', montant total '1500.00'
    Then le système valide l'importation et attribue le statut 'Pending Validation' à la facture

  Scenario: Importation d'une facture avec champ obligatoire manquant
    Given je suis sur la page "Importation des factures"
    When je tente d'importer une facture avec les champs suivants : identifiant fournisseur '', numéro de facture 'INV-2023-001', date de facture '2023-10-15', montant total '1500.00'
    Then je vois que le champ 'Identifiant fournisseur' est obligatoire lors de l'importation

  Scenario: Importation d'une facture avec montant total invalide
    Given je suis sur la page "Importation des factures"
    When je tente d'importer une facture avec les champs suivants : identifiant fournisseur 'SUPP001', numéro de facture 'INV-2023-001', date de facture '2023-10-15', montant total 'invalid'
    Then je vois que le champ 'montant total' affiche une erreur de format invalide lors de l'importation

  Scenario: Importation d'une facture dupliquée
    Given je suis sur la page "Importation des factures"
    When je tente d'importer une facture avec l'identifiant fournisseur 'SUPP001' et le numéro de facture 'INV-2023-001' déjà existants
    Then le système affiche un message d'erreur spécifique pour un doublon de facture avec le texte 'Cette facture existe déjà dans la base de données'
