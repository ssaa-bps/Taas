@id:SC-FAC-005 @module:Factures @exigence:SPEC-FAC-005
Feature: Consultation de factures importées

  Scenario: Consulter une facture importée
    Given je suis sur la page d'accueil
    When je clique sur le bouton "Factures" dans la barre d'actions
    Then je vois la liste des factures importées

  Scenario: Consulter les détails d'une facture importée
    Given je suis sur la page d'accueil
    When je clique sur le bouton "Factures" dans la barre d'actions
    And je sélectionne une facture dans la liste
    Then je vois les détails de la facture sélectionnée
