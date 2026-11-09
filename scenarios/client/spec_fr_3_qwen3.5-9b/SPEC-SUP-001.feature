@id:SC-SUP-001 @module:Supplier_Info_Management @exigence:SPEC-SUP-001
Feature: Gestion du cycle fournisseur dans Ivalua

  Scenario: Création d'une demande de référencement fournisseur avec toutes les informations obligatoires
    Given je crée une nouvelle demande de référencement fournisseur contenant la raison sociale, le pays, l'adresse, l'identifiant fiscal, le nom du contact principal, son adresse e-mail et la catégorie du fournisseur
    When je sauvegarde ma demande de référencement fournisseur en brouillon
    Then ma demande de référencement fournisseur est enregistrée en brouillon
