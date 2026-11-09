@id:SC-FRN-001 @module:Fournisseurs @exigence:SPEC-FRN-001
Feature: Création d'une demande de référencement fournisseur

  Scenario: Création d'une demande de référencement fournisseur complète en brouillon
    Given je suis sur la page de création de demande de référencement fournisseur
    When je crée une demande de référencement fournisseur avec les informations suivantes : raison sociale 'Acme Corp', pays 'France', adresse '123 Rue de la Paix', identifiant fiscal 'FR12345678900', contact principal 'Jean Dupont', email 'jean.dupont@acme.com' et catégorie 'Électronique'
    Then je sauvegarde la demande de référencement en brouillon

  Scenario: Création d'une demande de référencement fournisseur avec un champ obligatoire manquant (raison sociale)
    Given je suis sur la page de création de demande de référencement fournisseur
    When je remplis le champ raison sociale avec ''
    Then je vois que le champ 'raison sociale' affiche une erreur de champ vide dans la demande de référencement

  Scenario: Création d'une demande de référencement fournisseur avec un champ obligatoire manquant (pays)
    Given je suis sur la page de création de demande de référencement fournisseur
    When je remplis le champ raison sociale avec 'Acme Corp'
    Then je vois que le champ 'pays' affiche une erreur de champ vide dans la demande de référencement

  Scenario: Création d'une demande de référencement fournisseur avec un champ obligatoire manquant (adresse)
    Given je suis sur la page de création de demande de référencement fournisseur
    When je remplis le champ raison sociale avec 'Acme Corp' et le pays 'France'
    Then je vois que le champ 'adresse' affiche une erreur de champ vide dans la demande de référencement
