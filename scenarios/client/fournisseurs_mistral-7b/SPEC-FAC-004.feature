@id:SC-FAC-004 @module:Factures @exigence:SPEC-FAC-004
Feature: Gestion des factures fournisseurs

  Scenario: Facture en doublon
    Given je crée une facture avec les champs obligatoires identifiant fournisseur '{identifiant_fournisseur}' et numéro de facture '{numero_facture}'
    When je tente d'importer cette facture
    Then le système rejette la facture et affiche un message d'erreur spécifique pour un doublon de facture avec le texte 'Facture en doublon'
