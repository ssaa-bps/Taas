@id:SC-FRN-002 @module:Fournisseurs @exigence:SPEC-FRN-002
Feature: Gestion du cycle de vie des fournisseurs

  Scenario: Enregistrement d'une demande de référencement fournisseur en brouillon
    Given je suis un utilisateur habilité
    When je crée une demande de référencement fournisseur
    Then je vérifie que la demande est enregistrée en mode brouillon
