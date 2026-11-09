@id:SC-FRN-001 @module:Fournisseurs @exigence:SPEC-FRN-001
Feature: Création d'une demande de référencement fournisseur

  Scenario: Création complète d'une demande de référencement fournisseur
    Given je crée une demande de référencement fournisseur
    When je saisis la raison sociale dans le champ "SAS Transport SA"
    And je saisis le pays dans le champ "France"
    And je saisis l'adresse dans le champ "12 Rue de la République, Paris"
    And je saisis l'identifiant fiscal dans le champ "FR12345678901"
    And je saisis le nom du contact principal dans le champ "Jean Dupont"
    And je saisis l'adresse e-mail du contact principal dans le champ "jean.dupont@sas-transport.fr"
    And je sélectionne la catégorie du fournisseur "Logistique"
    And je enregistre la demande de référencement fournisseur en brouillon
    Then je vérifie que la demande est enregistrée en mode brouillon

  Scenario: Vérification des champs obligatoires marqués comme requis
    Given je crée une demande de référencement fournisseur
    When je vérifie que les champs obligatoires sont marqués comme requis dans l'interface

  Scenario: Validation de l'état de la demande après enregistrement en brouillon
    Given je crée une demande de référencement fournisseur
    When je saisis la raison sociale dans le champ "ABC Corp"
    And je enregistre la demande de référencement fournisseur en brouillon
    Then je vérifie que l'état de la demande est 'brouillon' après enregistrement
