@id:SC-ACH-003 @module:Achats @exigence:SPEC-ACH-003
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Création d'une demande d'achat avec calcul du montant total
    Given je suis sur la page d'achat
    When je remplis le champ quantité avec '{quantite}'
    And je remplis le champ prix unitaire avec '{prix_unitaire}'
    Then je vois que le montant total est calculé avec la valeur '{montant_total}'
