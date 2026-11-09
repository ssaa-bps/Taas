@id:SC-SUP-003 @module:Supplier_Info_Management @exigence:SPEC-SUP-003
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Le système ne considère pas comme soumise à validation une demande de référencement fournisseur enregistrée en brouillon
    Given je crée une nouvelle demande de référencement fournisseur
    When je sauvegarde ma demande de référencement fournisseur en brouillon
    Then le système ne considère pas comme soumise à validation toute demande de référencement fournisseur enregistrée en brouillon
