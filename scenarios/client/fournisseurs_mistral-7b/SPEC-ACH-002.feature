@id:SC-ACH-002 @module:Achats @exigence:SPEC-ACH-002
Feature: Gestion des demandes d'achat

  Scenario: Scénario nominal : la quantité et le prix unitaire doivent être strictement supérieurs à zéro
    Given je suis un employé habilité
    When je crée une demande d'achat avec la description '{description}', quantité '{quantite}', prix unitaire '{prix_unitaire}', fournisseur '{fournisseur}' et date de livraison '{date_livraison}'
    Then je vois que le statut de la demande d'achat est 'Pending Approval' et que le prix unitaire et la quantité sont strictement supérieurs à zéro

  Scenario: Scénario d'erreur : la quantité ou le prix unitaire sont invalides
    Given je suis un employé habilité
    When je tente de soumettre une demande d'achat avec une quantité ou un prix unitaire invalide
    Then je vois que le système empêche la soumission et affiche une erreur de valeur invalide
