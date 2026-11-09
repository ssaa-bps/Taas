@id:SC-FAC-001 @module:Factures @exigence:SPEC-FAC-001
Feature: Gestion des factures fournisseurs

  Scenario: Scénario nominal
    Given je suis un utilisateur habilité
    When je tente d'importer une facture avec les champs obligatoires remplis
    Then la facture est importée avec le statut 'Pending Validation'

  Scenario: Scénario d'erreur : facture avec champs obligatoires manquants
    Given je suis un utilisateur habilité
    When je tente d'importer une facture avec les champs obligatoires manquants

  Scenario: Scénario d'erreur : facture avec montant total invalide
    Given je suis un utilisateur habilité
    When je tente d'importer une facture avec un montant total invalide

  Scenario: Scénario d'erreur : facture déjà existante
    Given je suis un utilisateur habilité
    When je tente d'importer une facture avec un identifiant fournisseur et un numéro de facture déjà existants
