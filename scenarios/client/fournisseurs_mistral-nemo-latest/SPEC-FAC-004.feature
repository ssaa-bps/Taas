@id:SC-FAC-004 @module:Factures @exigence:SPEC-FAC-004
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Importer une facture valide et non dupliquée
    Given je suis sur l'écran de création de facture
    When je remplis le champ 'Identifiant fournisseur' avec une valeur valide
    And je remplis le champ 'Montant total' avec une valeur valide
    And je ne remplis pas les champs obligatoires manquants
    And je clique sur le bouton '{bouton}' dans la barre d'actions
    Then je vois que la facture est importée avec le statut « Pending Validation »
