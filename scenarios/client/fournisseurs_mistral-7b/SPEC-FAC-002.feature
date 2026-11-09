@id:SC-FAC-002 @module:Factures @exigence:SPEC-FAC-002
Feature: Gestion du cycle fournisseur dans Ivalua - Importation et traitement des factures fournisseurs

  Scenario: Scénario nominal
    Given je crée un fournisseur
    When je tente d'importer une facture avec les champs obligatoires remplis
    Then la facture est importée avec le statut 'Pending Validation'

  Scenario: Scénario de validation de montant total invalide
    Given je crée un fournisseur
    When je tente d'importer une facture avec un montant total invalide
    Then le système rejette la facture et affiche un message d'erreur spécifique

  Scenario: Scénario de validation de champs obligatoires manquants
    Given je crée un fournisseur
    When je tente d'importer une facture avec les champs obligatoires manquants
    Then le système rejette la facture et affiche un message d'erreur spécifique
