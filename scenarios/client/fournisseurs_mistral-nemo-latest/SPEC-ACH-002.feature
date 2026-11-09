@id:SC-ACH-002 @module:Achats @exigence:SPEC-ACH-002
Feature: Gestion des demandes d'achat

  Scenario: Création d'une demande d'achat avec des valeurs valides
    Given je suis sur la page de création de demande d'achat
    When je remplis le champ description avec '{description}'
    And je remplis le champ quantité avec '{quantite}'
    And je remplis le champ prix unitaire avec '{prix_unitaire}'
    And je remplis le champ fournisseur avec '{fournisseur}'
    And je remplis le champ date de livraison avec '{date_livraison}'
    And je clique sur le bouton 'Enregistrer'
    Then je vois que la demande d'achat est créée avec succès

  Scenario: Création d'une demande d'achat avec une quantité non supérieure à zéro
    Given je suis sur la page de création de demande d'achat
    When je remplis le champ quantité avec '{0}'
    And je remplis les autres champs avec des valeurs valides
    And je clique sur le bouton 'Enregistrer'
    Then je vois une erreur indiquant que la quantité doit être strictement supérieure à zéro

  Scenario: Création d'une demande d'achat avec un prix unitaire non supérieur à zéro
    Given je suis sur la page de création de demande d'achat
    When je remplis le champ prix unitaire avec '{0}'
    And je remplis les autres champs avec des valeurs valides
    And je clique sur le bouton 'Enregistrer'
    Then je vois une erreur indiquant que le prix unitaire doit être strictement supérieur à zéro
