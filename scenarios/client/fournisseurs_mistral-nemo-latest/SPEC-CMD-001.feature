@id:SC-CMD-001 @module:Commandes @exigence:SPEC-CMD-001
Feature: Gestion des commandes d'achat

  Scenario: Création d'une commande d'achat à partir d'une demande d'achat approuvée
    Given je suis sur la page de la demande d'achat approuvée '{numéro_demande}'
    When je clique sur le bouton 'Convertir en commande'
    Then je vois que la commande d'achat est créée avec le numéro unique '{numéro_commande}' et le statut 'Pending Dispatch'

  Scenario: Empêchement de créer plusieurs commandes d'achat à partir d'une même demande d'achat
    Given je suis sur la page de la demande d'achat approuvée '{numéro_demande}'
    When je clique sur le bouton 'Convertir en commande' plusieurs fois
    Then je vois une alerte indiquant qu'une seule commande peut être générée à partir d'une même demande d'achat
