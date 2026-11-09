@id:SC-FRN-002 @module:Fournisseurs @exigence:SPEC-FRN-002
Feature: Enregistrement d'une demande de référencement fournisseur en brouillon

  Scenario: Enregistrement complet d'une demande de référencement en brouillon avec tous les champs obligatoires
    Given je crée une demande de référencement fournisseur
    When je saisis la raison sociale dans le champ "Ivalua GmbH"
    And je saisis le pays dans le champ "Allemagne"
    And je saisis l'adresse dans le champ "Musterstraße 1, Berlin"
    And je saisis l'identifiant fiscal dans le champ "DE123456789"
    And je saisis le nom du contact principal dans le champ "Max Mustermann"
    And je saisis l'adresse e-mail du contact principal dans le champ "max.mustermann@ivalua.com"
    And je sélectionne la catégorie du fournisseur "Services IT"
    And je enregistre la demande de référencement fournisseur en brouillon
    Then je vérifie que la demande est enregistrée en mode brouillon
    And je valide que la demande est sauvegardée après enregistrement en brouillon
    And je vérifie que l'état de la demande est 'brouillon' après enregistrement

  Scenario: Enregistrement d'une demande de référencement en brouillon avec champ obligatoire manquant
    Given je crée une demande de référencement fournisseur
    When je saisis la raison sociale dans le champ "Ivalua GmbH"
    And je saisis le pays dans le champ "Allemagne"
    And je saisis l'adresse dans le champ "Musterstraße 1, Berlin"
    And je saisis l'identifiant fiscal dans le champ "DE123456789"
    And je saisis le nom du contact principal dans le champ "Max Mustermann"
    And je saisis l'adresse e-mail du contact principal dans le champ ""
    And je sélectionne la catégorie du fournisseur "Services IT"
    And je enregistre la demande de référencement fournisseur en brouillon
    Then je vérifie que les champs obligatoires sont marqués comme requis dans l'interface
