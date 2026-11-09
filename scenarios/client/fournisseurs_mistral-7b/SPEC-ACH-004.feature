@id:SC-ACH-004 @module:Achats @exigence:SPEC-ACH-004
Feature: Gestion des demandes d'achat

  Scenario: Enregistrement d'une demande d'achat en brouillon
    Given je suis un employé habilité
    And je crée une demande d'achat avec la description '{description}', quantité '{quantite}', prix unitaire '{prix_unitaire}', fournisseur '{fournisseur}' et date de livraison '{date_livraison}'
    When je tente de soumettre la demande d'achat
    Then je vois que le statut de la demande d'achat est 'En brouillon'

  Scenario: Soumission d'une demande d'achat
    Given je suis un employé habilité
    And je crée une demande d'achat avec la description '{description}', quantité '{quantite}', prix unitaire '{prix_unitaire}', fournisseur '{fournisseur}' et date de livraison '{date_livraison}'
    When je soumet la demande d'achat
    Then je vois que le statut de la demande d'achat est 'Pending Approval'

  Scenario: Soumission d'une demande d'achat avec un champ obligatoire manquant
    Given je suis un employé habilité
    And je crée une demande d'achat avec la description '{description}', quantité '{quantite}', prix unitaire '{prix_unitaire}', fournisseur '{fournisseur}' et date de livraison '{date_livraison}'
    When je tente de soumettre la demande d'achat avec un champ obligatoire manquant
    Then je vois que le système empêche la soumission

  Scenario: Soumission d'une demande d'achat avec une quantité ou un prix unitaire invalide
    Given je suis un employé habilité
    And je crée une demande d'achat avec la description '{description}', quantité '{quantite}', prix unitaire '{prix_unitaire}', fournisseur '{fournisseur}' et date de livraison '{date_livraison}'
    When je tente de soumettre la demande d'achat avec une quantité ou un prix unitaire invalide
    Then je vois que le système empêche la soumission
