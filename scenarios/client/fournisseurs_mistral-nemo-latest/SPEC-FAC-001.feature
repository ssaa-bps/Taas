@id:SC-FAC-001 @module:Factures @exigence:SPEC-FAC-001
Feature: Facture fournisseur

  Scenario: Rejet de facture avec champs obligatoires manquants
    Given je tente d'importer une facture avec les champs obligatoires manquants
    When je clique sur le bouton "Importer"
    Then je vois une alerte indiquant que les champs obligatoires sont manquants

  Scenario: Rejet de facture avec montant total invalide
    Given je tente d'importer une facture avec un montant total invalide
    When je clique sur le bouton "Importer"
    Then je vois une alerte indiquant que le montant total est invalide
