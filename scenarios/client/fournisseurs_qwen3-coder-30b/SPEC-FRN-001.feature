@id:SC-FRN-001 @module:Fournisseurs @exigence:SPEC-FRN-001
Feature: Création d'une demande de référencement fournisseur

  Scenario: Création d'une demande de référencement fournisseur avec tous les champs obligatoires remplis
    Given je suis sur la page "Création de demande de référencement fournisseur"
    When je remplis le champ raison sociale avec 'Acme Inc'
    And je remplis le champ pays avec 'France'
    And je remplis le champ adresse avec '123 Rue de la Paix'
    And je remplis le champ identifiant fiscal avec 'FR123456789'
    And je remplis le champ contact principal avec 'Jean Dupont'
    And je remplis le champ email avec 'jean.dupont@acme.com'
    And je remplis le champ catégorie avec 'Fournisseur principal'
    And je clique sur le bouton 'Enregistrer en brouillon'
    Then le système affiche un message indiquant que la demande de référencement fournisseur est en statut 'Brouillon'

  Scenario: Tentative de création d'une demande de référencement fournisseur sans remplir les champs obligatoires
    Given je suis sur la page "Création de demande de référencement fournisseur"
    When je clique sur le bouton 'Enregistrer en brouillon' sans remplir aucun champ
    Then le système affiche une erreur pour chaque champ obligatoire non rempli

  Scenario: Création d'une demande de référencement fournisseur avec un email invalide
    Given je suis sur la page "Création de demande de référencement fournisseur"
    When je remplis le champ raison sociale avec 'Acme Inc'
    And je remplis le champ pays avec 'France'
    And je remplis le champ adresse avec '123 Rue de la Paix'
    And je remplis le champ identifiant fiscal avec 'FR123456789'
    And je remplis le champ contact principal avec 'Jean Dupont'
    And je remplis le champ email avec 'email.invalide'
    And je remplis le champ catégorie avec 'Fournisseur principal'
    And je clique sur le bouton 'Enregistrer en brouillon'
    Then le système affiche une erreur de format invalide pour le champ email
