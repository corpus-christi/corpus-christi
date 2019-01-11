describe("Home page", function() {
  it("successfully loads", function() {
    cy.visit("/");
  });
});

describe("Tool bar", function() {
  it("links to the I18N page", function() {
    cy.get('[href="/locale"]').click();
    cy.url().should("include", "/locale");
    cy.contains("Locales");
  });
});
