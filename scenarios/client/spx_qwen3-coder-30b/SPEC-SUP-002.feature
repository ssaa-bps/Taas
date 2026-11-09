@id:SC-SUP-002 @module:sup @exigence:SPEC-SUP-002
Feature: Enregistrement d'une demande de référencement fournisseur en brouillon

  Scenario: Enregistrement d'une demande de référencement fournisseur en brouillon
    Given je crée une demande de référencement fournisseur
    When je sauvegarde ma demande de référencement fournisseur en brouillon
    Then ma demande de référencement fournisseur est enregistrée en brouillon

  Scenario: Vérification que la demande en brouillon n'est pas soumise à validation
    Given je crée une demande de référencement fournisseur
    When je sauvegarde ma demande de référencement fournisseur en brouillon
    Then le système ne considère pas comme soumise à validation toute demande de référencement fournisseur enregistrée en brouillon
