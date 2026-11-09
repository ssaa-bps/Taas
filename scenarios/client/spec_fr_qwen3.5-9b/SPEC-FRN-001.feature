@id:SC-FRN-001 @module:Fournisseurs @exigence:SPEC-FRN-001
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Création d'une demande de référencement fournisseur complète
    Given je crée une demande de référencement fournisseur
    When je saisis "raison sociale" dans le champ "raison_sociale"
    And je saisis "France" dans le champ "pays"
    And je saisis "123 Rue de l'Exemple" dans le champ "adresse"
    And je saisis "FR123456789" dans le champ "identifiant_fiscal"
    And je saisis "Jean Dupont" dans le champ "nom_contact"
    And je saisis "jean.dupont@exemple.com" dans le champ "email_contact"
    And je sélectionne "Électronique" dans la liste "categorie_fournisseur"
    Then ma demande de référencement fournisseur est enregistrée en brouillon
