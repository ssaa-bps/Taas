@id:SC-FRN-001 @module:Fournisseurs @exigence:SPEC-FRN-001
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Création d'une demande de référencement fournisseur
    Given je suis sur la page de création de demande de référencement fournisseur
    When je remplis le champ raison sociale avec '{raison_sociale}'
    And je remplis le champ pays avec '{pays}'
    And je remplis le champ adresse avec '{adresse}'
    And je remplis le champ identifiant fiscal avec '{identifiant_fiscal}'
    And je remplis le champ contact principal avec '{contact}'
    And je remplis le champ email avec '{email}'
    And je remplis le champ catégorie avec '{categorie}'
    And je clique sur le bouton 'Enregistrer en brouillon'
    Then je vois que la demande de référencement est en statut 'Brouillon'
