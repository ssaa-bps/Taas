@id:SC-FRN-001 @module:Fournisseurs @exigence:SPEC-FRN-001
Feature: Gestion du cycle de vie des fournisseurs

  Scenario: Création d'une demande de référencement fournisseur complète
    Given je crée une demande de référencement fournisseur
    When je remplis le champ 'firm name' avec la valeur '{firm_name}'
    And je remplis le champ 'pays' avec '{pays}'
    And je remplis le champ 'adresse' avec '{adresse}'
    And je remplis le champ 'numéro de taxe' avec '{numero_taxe}'
    And je remplis le champ 'nom du principal contact' avec '{nom_contact}'
    And je remplis le champ 'email du contact' avec '{email_contact}'
    And je sélectionne l'option '{categorie_fournisseur}' dans la liste déroulante de catégorie
    Then je valide que la demande est sauvegardée après enregistrement en brouillon
