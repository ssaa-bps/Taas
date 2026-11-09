@id:SC-FRN-002 @module:Fournisseurs @exigence:SPEC-FRN-002
Feature: Référencement fournisseur - Enregistrement en brouillon

  Scenario: Enregistrement d'une demande de référencement fournisseur complète en brouillon
    Given je suis sur la page de création de demande de référencement fournisseur
    When je crée une demande de référencement fournisseur avec les informations suivantes : raison sociale 'Acme Corp', pays 'France', adresse '123 Rue de l'Innovation', identifiant fiscal 'FR12345678901', contact principal 'Jean Dupont', email 'jean.dupont@acme.com' et catégorie 'Technologie'
    And je sauvegarde la demande de référencement en brouillon
    Then je vois que la demande de référencement est en statut 'Brouillon'
    And je vois que la demande de référencement n'est pas soumise à validation

  Scenario: Enregistrement d'une demande de référencement fournisseur vide en brouillon pour complétion ultérieure
    Given je suis sur la page de création de demande de référencement fournisseur
    When je sauvegarde une demande de référencement fournisseur avec le statut 'Brouillon' sans validation automatique
    Then je vois que la demande de référencement est en statut 'Brouillon'
    And je vois que la demande de référencement n'est pas soumise à validation

  Scenario: Enregistrement d'une demande de référencement fournisseur en brouillon puis complétion ultérieure
    Given je suis sur la page de création de demande de référencement fournisseur
    When je sauvegarde une demande de référencement fournisseur avec le statut 'Brouillon' sans validation automatique
    Then je vois que la demande de référencement est en statut 'Brouillon'
    When je complète une demande de référencement en brouillon avec les informations suivantes : raison sociale 'TechSolutions Ltd', pays 'Royaume-Uni', adresse '45 High Street', identifiant fiscal 'GB98765432109', contact principal 'Sarah Smith', email 'sarah.smith@techsolutions.co.uk' et catégorie 'Logiciel'
    Then je vois que la demande de référencement est en statut 'Brouillon'
