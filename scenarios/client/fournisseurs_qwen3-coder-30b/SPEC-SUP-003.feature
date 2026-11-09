@id:SC-SUP-003 @module:sup @exigence:SPEC-SUP-003
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Complétion ultérieure d'une demande de référencement fournisseur en brouillon
    Given je crée une demande de référencement fournisseur
    When je sauvegarde ma demande de référencement fournisseur en brouillon
    Then ma demande de référencement fournisseur est enregistrée en brouillon

  Scenario: Validation que la demande en brouillon n'est pas soumise à validation
    Given je crée une demande de référencement fournisseur
    When je sauvegarde ma demande de référencement fournisseur en brouillon
    Then le système ne considère pas comme soumise à validation toute demande de référencement fournisseur enregistrée en brouillon

  Scenario: Complétion ultérieure d'une demande de référencement fournisseur en brouillon
    Given je crée une demande de référencement fournisseur
    When je sauvegarde ma demande de référencement fournisseur en brouillon
    Then je complète ultérieurement une demande de référencement fournisseur en brouillon

  Scenario: Vérification du statut de la demande en brouillon
    Given je crée une demande de référencement fournisseur
    When je sauvegarde ma demande de référencement fournisseur en brouillon
    Then le statut de "demande de référencement fournisseur" est "en brouillon"
