@id:SC-FRN-002 @module:Fournisseurs @exigence:SPEC-FRN-002
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Enregistrement d'une demande de référencement fournisseur en brouillon
    Given je suis un utilisateur habilité
    When je crée une demande de référencement fournisseur
    And je enregistre la demande de référencement fournisseur en brouillon
    Then la demande est enregistrée en brouillon et peut être complétée ultérieurement
