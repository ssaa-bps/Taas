@id:SC-ACH-002 @module:Achats @exigence:SPEC-ACH-002
Feature: Gestion des demandes d'achat

  Scenario: Enregistrement d'une demande d'achat en brouillon - Scénario nominal
    Given je suis sur la page "Création de demande d'achat"
    When je crée une demande d'achat avec la description "Test", quantité "10", prix unitaire "50.00", fournisseur "Fournisseur Test" et date de livraison "2025-12-31"
    And je sauvegarde la demande d'achat en brouillon
    Then je vois que le statut de la demande d'achat est 'Brouillon'

  Scenario: Enregistrement d'une demande d'achat en brouillon - Champ obligatoire manquant
    Given je suis sur la page "Création de demande d'achat"
    When je remplis le champ description avec 'Test'
    And je ne remplis pas le champ quantité
    And je clique sur le bouton 'Enregistrer en brouillon'
    Then le champ 'quantité' affiche une erreur de valeur invalide dans la demande d'achat

  Scenario: Enregistrement d'une demande d'achat en brouillon - Quantité non strictement supérieure à zéro
    Given je suis sur la page "Création de demande d'achat"
    When je remplis le champ description avec 'Test'
    And je remplis le champ quantité avec '0'
    And je clique sur le bouton 'Enregistrer en brouillon'
    Then le champ 'quantité' affiche une erreur de valeur invalide dans la demande d'achat

  Scenario: Enregistrement d'une demande d'achat en brouillon - Prix unitaire non strictement supérieure à zéro
    Given je suis sur la page "Création de demande d'achat"
    When je remplis le champ description avec 'Test'
    And je remplis le champ prix unitaire avec '0'
    And je clique sur le bouton 'Enregistrer en brouillon'
    Then le champ 'prix unitaire' affiche une erreur de valeur invalide dans la demande d'achat
