@id:SC-ACH-001 @module:Achats @exigence:SPEC-ACH-001
Feature: Création d'une demande d'achat

  Scenario: Création d'une demande d'achat valide
    Given je suis sur la page "Création de demande d'achat"
    When je crée une demande d'achat avec la description "Imprimante Laser", quantité "10", prix unitaire "150.00", fournisseur "ABC Supplies" et date de livraison "2024-06-15"
    Then je vois que le montant total est calculé à "1500.00"

  Scenario: Tentative de création d'une demande d'achat avec quantité invalide
    Given je suis sur la page "Création de demande d'achat"
    When je crée une demande d'achat avec la description "Imprimante Laser", quantité "0", prix unitaire "150.00", fournisseur "ABC Supplies" et date de livraison "2024-06-15"
    Then je vois que le champ "quantité" affiche une erreur de valeur invalide dans la demande d'achat

  Scenario: Tentative de création d'une demande d'achat avec prix unitaire invalide
    Given je suis sur la page "Création de demande d'achat"
    When je crée une demande d'achat avec la description "Imprimante Laser", quantité "10", prix unitaire "0.00", fournisseur "ABC Supplies" et date de livraison "2024-06-15"
    Then je vois que le champ "prix unitaire" affiche une erreur de valeur invalide dans la demande d'achat

  Scenario: Tentative de création d'une demande d'achat sans description
    Given je suis sur la page "Création de demande d'achat"
    When je crée une demande d'achat avec la description "", quantité "10", prix unitaire "150.00", fournisseur "ABC Supplies" et date de livraison "2024-06-15"
    Then je vois que le champ "description" est obligatoire dans la demande d'achat
