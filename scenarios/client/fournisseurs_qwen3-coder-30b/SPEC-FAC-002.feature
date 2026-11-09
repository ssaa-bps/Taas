@id:SC-FAC-002 @module:Factures @exigence:SPEC-FAC-002
Feature: Consultation des détails d'une facture importée

  Scenario: Consultation réussie des détails d'une facture importée valide
    Given je suis sur l'écran de création de facture
    When je tente d'importer une facture avec les champs suivants : identifiant fournisseur 'SUPP001', numéro de facture 'INV-2023-001', date de facture '2023-10-15', montant total '1500.00'
    Then le système valide l'importation et attribue le statut 'Pending Validation' à la facture
    And je consulte les détails de la facture importée avec le numéro de facture 'INV-2023-001'
    And je vois que le statut de la facture est 'Pending Validation'
    And je vois que la facture importée contient l'identifiant fournisseur 'SUPP001'
    And je vois que la facture importée contient le numéro de facture 'INV-2023-001'
    And je vois que la facture importée contient la date de facture '2023-10-15'
    And je vois que la facture importée contient le montant total '1500.00'

  Scenario: Consultation des détails d'une facture dupliquée
    Given je suis sur l'écran de création de facture
    When je tente d'importer une facture avec les champs suivants : identifiant fournisseur 'SUPP001', numéro de facture 'INV-2023-001', date de facture '2023-10-15', montant total '1500.00'
    Then le système valide l'importation et attribue le statut 'Pending Validation' à la facture
    And je tente d'importer une facture avec les mêmes champs : identifiant fournisseur 'SUPP001', numéro de facture 'INV-2023-001', date de facture '2023-10-15', montant total '1500.00'
    And je consulte les détails de la facture importée avec le numéro de facture 'INV-2023-001'
    And je vois que le statut de la facture est 'Pending Validation' après validation
