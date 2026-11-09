@id:SC-FAC-002 @module:Factures @exigence:SPEC-FAC-002
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Vérifier l'unicité d'une facture avant importation
    Given je suis sur l'écran de création de facture
    When je tente d'importer une facture avec un identifiant fournisseur et un numéro de facture déjà existants
    Then je vois une alerte indiquant que la facture est un doublon
