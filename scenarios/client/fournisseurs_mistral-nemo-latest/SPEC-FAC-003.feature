@id:SC-FAC-003 @module:Factures @exigence:SPEC-FAC-003
Feature: Gestion des factures fournisseurs

  Scenario: Rejet d'une facture en doublon
    Given je tente d'importer une facture avec un identifiant fournisseur et un numéro de facture déjà existants
    When je clique sur le bouton "Importer"
    Then je vois une alerte indiquant que la facture est un doublon
