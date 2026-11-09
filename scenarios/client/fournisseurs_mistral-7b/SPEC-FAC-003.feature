@id:SC-FAC-003 @module:Factures @exigence:SPEC-FAC-003
Feature: Gestion du cycle fournisseur dans Ivalua - Importation de factures fournisseurs

  Scenario: Scénario nominal
    Given je crée un fournisseur avec l'identifiant '{identifiant_fournisseur}'
    When je tente d'importer une facture avec l'identifiant fournisseur '{identifiant_fournisseur}' et le numéro de facture '{numero_facture}'
    Then le système vérifie si une facture portant le même identifiant fournisseur et le même numéro de facture existe déjà

  Scenario: Scénario de doublon de facture
    Given je crée un fournisseur avec l'identifiant '{identifiant_fournisseur}'
    When je tente d'importer une facture avec l'identifiant fournisseur '{identifiant_fournisseur}' et le numéro de facture '{numero_facture}' déjà existant
    Then le système rejette la facture et affiche un message d'erreur spécifique pour un doublon de facture
