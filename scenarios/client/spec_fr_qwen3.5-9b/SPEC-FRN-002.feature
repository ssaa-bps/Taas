@id:SC-FRN-002 @module:Fournisseurs @exigence:SPEC-FRN-002
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Enregistrement d'une demande de référencement fournisseur en brouillon
    Given je crée une demande de référencement fournisseur
    When je sauvegarde ma demande de référencement fournisseur en brouillon
    Then ma demande de référencement fournisseur est enregistrée en brouillon
