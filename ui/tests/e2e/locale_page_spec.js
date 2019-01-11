describe("Locale page", function() {
  it("contains test locales", function() {
    cy.visit("/locale");
    cy.contains("Locales");
    cy.get('[data-cy="locale-select"]')
      .parent()
      .click();
  });
});
