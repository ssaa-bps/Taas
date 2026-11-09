@id:SC-SUP-001 @module:Supplier_Info_Management @exigence:SPEC-SUP-001
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Création d'une demande de référencement fournisseur complète
    Given je crée une nouvelle demande de référencement fournisseur
    When je saisis "raison sociale" dans le champ "champ"
    And je saisis "pays" dans le champ "champ"
    And je saisis "adresse" dans le champ "champ"
    And je saisis "identifiant fiscal" dans le champ "champ"
    And je saisis "nom du contact principal" dans le champ "champ"
    And je saisis "adresse e-mail" dans le champ "champ"
    And je sélectionne "catégorie du fournisseur" dans la liste "liste"
    Then ma demande de référencement fournisseur est enregistrée en brouillon
