@id:SC-ACH-001 @module:Achats @exigence:SPEC-ACH-001
Feature: Gestion des demandes d'achat

  Scenario: Création d'une demande d'achat
    Given je suis sur la page de création de demande d'achat
    When je remplis le champ description avec '{texte}'
    And je remplis le champ quantité avec '{nombre}'
    And je remplis le champ prix unitaire avec '{montant}'
    And je remplis le champ fournisseur avec '{nom}'
    And je remplis le champ date de livraison avec '{date}'
    And je clique sur le bouton 'Enregistrer'
    Then je vois que la demande d'achat est créée avec les informations fournies
