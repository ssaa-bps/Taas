@id:SC-SUP-001 @module:sup @exigence:SPEC-SUP-001
Feature: Création d'une demande de référencement fournisseur

  Scenario: Création d'une demande de référencement fournisseur avec tous les champs requis
    Given je crée une nouvelle demande de référencement fournisseur
    When je saisis "Raison Sociale Test" dans le champ "raison sociale"
    And je saisis "France" dans le champ "pays"
    And je saisis "123 Rue de Test" dans le champ "adresse"
    And je saisis "FR123456789" dans le champ "identifiant fiscal"
    And je saisis "Jean Dupont" dans le champ "nom du contact principal"
    And je saisis "jean.dupont@test.com" dans le champ "adresse e-mail du contact principal"
    And je sélectionne "Catégorie A" dans la liste "catégorie du fournisseur"
    Then je crée une nouvelle demande de référencement fournisseur contenant la raison sociale, le pays, l'adresse, l'identifiant fiscal, le nom du contact principal, son adresse e-mail et la catégorie du fournisseur
