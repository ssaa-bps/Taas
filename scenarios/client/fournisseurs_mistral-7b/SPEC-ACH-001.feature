@id:SC-ACH-001 @module:Achats @exigence:SPEC-ACH-001
Feature: Gestion des demandes d'achat

  Scenario: Scénario nominal
    Given je suis un employé habilité
    When je crée une demande d'achat avec la description '{description}', quantité '{quantite}', prix unitaire '{prix_unitaire}', fournisseur '{fournisseur}' et date de livraison '{date_livraison}'
    Then je vois que la demande d'achat est créée avec les informations fournies

  Scenario: Scénario de validation de champ obligatoire manquant
    Given je suis un employé habilité
    When je tente de soumettre une demande d'achat avec un champ obligatoire manquant
    Then je vois que le système empêche la soumission de la demande d'achat

  Scenario: Scénario de validation de quantité ou prix unitaire invalide
    Given je suis un employé habilité
    When je tente de soumettre une demande d'achat avec une quantité ou un prix unitaire invalide
    Then je vois que le système empêche la soumission de la demande d'achat

  Scenario: Scénario de validation de date de livraison manquante
    Given je suis un employé habilité
    When je tente de soumettre une demande d'achat avec une date de livraison manquante
    Then je vois que le système empêche la soumission de la demande d'achat
