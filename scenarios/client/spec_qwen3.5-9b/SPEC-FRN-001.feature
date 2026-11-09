@id:SC-FRN-001 @module:Fournisseurs @exigence:SPEC-FRN-001
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Création d'une demande de référencement fournisseur complète
    Given je suis un utilisateur habilité
    When je crée une demande de référencement fournisseur
    And je saisis la raison sociale dans le champ "{raison_sociale}"
    And je saisis le pays dans le champ "{pays}"
    And je saisis l'adresse dans le champ "{adresse}"
    And je saisis l'identifiant fiscal dans le champ "{identifiant_fiscal}"
    And je saisis le nom du contact principal dans le champ "{nom_contact_principal}"
    And je saisis l'adresse e-mail du contact principal dans le champ "{email_contact_principal}"
    And je sélectionne la catégorie du fournisseur "{categorie_fournisseur}"
    Then la demande de référencement fournisseur est créée avec succès
