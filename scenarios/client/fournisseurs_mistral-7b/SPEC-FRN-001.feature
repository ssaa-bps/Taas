@id:SC-FRN-001 @module:Fournisseurs @exigence:SPEC-FRN-001
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Scénario nominal : création d'une demande de référencement fournisseur
    Given je suis un utilisateur habilité
    When je crée une demande de référencement fournisseur avec les informations suivantes : raison sociale '{raison_sociale}', pays '{pays}', adresse '{adresse}', identifiant fiscal '{identifiant_fiscal}', contact principal '{contact}', email '{email}' et catégorie '{categorie}'
    Then la demande de référencement fournisseur est créée avec succès

  Scenario: Scénario de validation : création d'une demande de référencement fournisseur avec un champ obligatoire manquant
    Given je suis un utilisateur habilité
    When je crée une demande de référencement fournisseur avec un champ obligatoire manquant
    Then une erreur est affichée pour le champ manquant
