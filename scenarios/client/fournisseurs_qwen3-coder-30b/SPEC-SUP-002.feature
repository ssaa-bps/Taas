@id:SC-SUP-002 @module:sup @exigence:SPEC-SUP-002
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Enregistrement d'une demande de référencement fournisseur en brouillon
    Given je crée une demande de référencement fournisseur
    When je sauvegarde ma demande de référencement fournisseur en brouillon
    Then ma demande de référencement fournisseur est enregistrée en brouillon
