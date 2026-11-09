@id:SC-FRN-003 @module:Fournisseurs @exigence:SPEC-FRN-003
Feature: Gestion de l'état des demandes de référencement fournisseur

  Scenario: Scénario : Tentative de soumission d'une demande en brouillon
    Given je crée une demande de référencement fournisseur
    When je saisis la raison sociale dans le champ "Acme SA"
    And je saisis le pays dans le champ "France"
    And je saisis l'adresse dans le champ "123 Rue de Paris, Paris"
    And je saisis l'identifiant fiscal dans le champ "FR12345678901"
    And je saisis le nom du contact principal dans le champ "Jean Dupont"
    And je saisis l'adresse e-mail du contact principal dans le champ "jean.dupont@acme.com"
    And je sélectionne la catégorie du fournisseur "Services"
    And je enregistre la demande de référencement fournisseur en brouillon
    And je tente de soumettre la demande enregistrée en brouillon pour validation
    Then le système affiche un message d'erreur indiquant que la demande n'est pas prête pour validation
