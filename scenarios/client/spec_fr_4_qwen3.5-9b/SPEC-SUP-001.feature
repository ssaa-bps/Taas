@id:SC-SUP-001 @module:sup @exigence:SPEC-SUP-001
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Création d'une demande de référencement fournisseur complète
    Given je crée une nouvelle demande de référencement fournisseur
    When je saisis "raison sociale" dans le champ "raison sociale"
    And je saisis "France" dans le champ "pays"
    And je saisis "123 Rue de l'Exemple" dans le champ "adresse"
    And je saisis "FR123456789" dans le champ "identifiant fiscal"
    And je saisis "Jean Dupont" dans le champ "nom du contact principal"
    And je saisis "jean.dupont@exemple.com" dans le champ "adresse e-mail"
    And je sélectionne "Électronique" dans la liste "catégorie du fournisseur"
    Then ma demande de référencement fournisseur est enregistrée en brouillon
