@id:SC-FAC-006 @module:Factures @exigence:SPEC-FAC-006
Feature: Consultation de factures fournisseurs

  Scenario: Consultation d'une facture importée
    Given une facture est importée
    When je consulte la facture
    Then je peux voir les détails de la facture

  Scenario: Consultation d'une facture importée avec erreur
    Given une facture a été importée avec erreur
    When je consulte la facture
    Then je peux voir les détails de la facture et l'erreur
