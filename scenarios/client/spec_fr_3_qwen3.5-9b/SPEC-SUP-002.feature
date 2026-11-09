@id:SC-SUP-002 @module:Supplier_Info_Management @exigence:SPEC-SUP-002
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Enregistrement d'une demande de référencement fournisseur en brouillon
    Given je crée une nouvelle demande de référencement fournisseur
    When je sauvegarde ma demande de référencement fournisseur en brouillon
    Then ma demande de référencement fournisseur est enregistrée en brouillon

  Scenario: Vérification que la demande en brouillon n'est pas soumise à validation
    Given je sauvegarde ma demande de référencement fournisseur en brouillon
    Then le système ne considère pas comme soumise à validation toute demande de référencement fournisseur enregistrée en brouillon
