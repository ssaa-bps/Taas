@id:SC-ACH-003 @module:Achats @exigence:SPEC-ACH-003
Feature: Gestion des demandes d'achat

  Scenario: Calcul du montant total
    Given je crée une demande d'achat avec la description '{description}', quantité '{quantite}', prix unitaire '{prix_unitaire}', fournisseur '{fournisseur}' et date de livraison '{date_livraison}'
    When je soumet la demande d'achat
    Then le système calcule le montant total en multipliant la quantité par le prix unitaire
