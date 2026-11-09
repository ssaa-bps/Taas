@id:SC-ACH-004 @module:Achats @exigence:SPEC-ACH-004
Feature: Gestion des demandes d'achat

  Scenario: Approbation d'une demande d'achat par un approbateur habilité
    Given je suis connecté en tant qu'approbateur habilité
    When je sélectionne une demande d'achat en attente d'approbation
    And je clique sur le bouton 'Approuver'
    Then je vois que le statut de la demande d'achat est passé à 'Approved'

  Scenario: Rejet d'une demande d'achat par un approbateur habilité
    Given je suis connecté en tant qu'approbateur habilité
    When je sélectionne une demande d'achat en attente d'approbation
    And je clique sur le bouton 'Rejeter'
    Then je vois que le statut de la demande d'achat est passé à 'Rejected'
