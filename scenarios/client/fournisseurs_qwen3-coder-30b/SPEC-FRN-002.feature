@id:SC-FRN-002 @module:Fournisseurs @exigence:SPEC-FRN-002
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Enregistrement d'une demande de référencement en brouillon - Scénario nominal
    Given je suis sur la page "Création de demande de référencement fournisseur"
    When je crée une demande de référencement fournisseur avec les informations suivantes : raison sociale 'Acme Corp', pays 'France', adresse '123 Rue de la Paix', identifiant fiscal 'FR123456789', contact principal 'Jean Dupont', email 'jean.dupont@acme.com' et catégorie 'Technologie'
    And je clique sur le bouton "Enregistrer en brouillon"
    Then je vois que la demande de référencement est en statut 'Brouillon'

  Scenario: Enregistrement d'une demande de référencement en brouillon - Champ requis manquant
    Given je suis sur la page "Création de demande de référencement fournisseur"
    When je remplis le champ raison sociale avec 'Acme Corp'
    And je ne remplis pas le champ email
    And je clique sur le bouton "Enregistrer en brouillon"
    Then je vois que le champ 'email' affiche une erreur de champ vide lors de la validation
