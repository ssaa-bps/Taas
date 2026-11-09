@id:SC-FRN-002 @module:Fournisseurs @exigence:SPEC-FRN-002
Feature: Gestion du cycle fournisseur dans Ivalua - Référencement fournisseur

  Scenario: Enregistrement d'une demande de référencement en brouillon
    Given je suis un utilisateur habilité
    When je crée une demande de référencement fournisseur avec le statut 'Brouillon'
    Then je peux enregistrer la demande en brouillon

  Scenario: Enregistrement d'une demande de référencement en brouillon avec des champs obligatoires manquants
    Given je suis un utilisateur habilité
    When je crée une demande de référencement fournisseur avec le statut 'Brouillon' et un champ obligatoire manquant
    Then le système affiche un message d'erreur spécifique pour un champ manquant

  Scenario: Enregistrement d'une demande de référencement en brouillon avec un champ obligatoire invalide
    Given je suis un utilisateur habilité
    When je crée une demande de référencement fournisseur avec un champ obligatoire invalide
    Then le système affiche un message d'erreur spécifique pour un champ invalide

  Scenario: Enregistrement d'une demande de référencement en brouillon avec des champs obligatoires remplis
    Given je suis un utilisateur habilité
    When je crée une demande de référencement fournisseur avec les champs obligatoires remplis
    Then je peux enregistrer la demande en brouillon
