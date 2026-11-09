@id:SC-FAC-005 @module:Factures @exigence:SPEC-FAC-005
Feature: Gestion du cycle fournisseur dans Ivalua - Importation et traitement des factures fournisseurs

  Scenario: Scénario nominal
    Given je crée un fournisseur avec les identifiants '{identifiant_fournisseur}' et '{numero_facture}'
    When je tente d'importer une facture avec les champs obligatoires remplis et un montant total valide
    Then la facture est importée avec le statut 'Pending Validation'

  Scenario: Scénario de doublon
    Given je crée un fournisseur avec les identifiants '{identifiant_fournisseur}' et '{numero_facture}'
    When je tente d'importer une facture avec les mêmes identifiants et un montant total valide
    Then une erreur d'erreur d'importation est affichée
