//Tests logging in and going to the people page
describe("Tests the user navigation to the people page", function() {
  it("Given: logs in successfully", function() {
    cy.login();
    cy.url().should("include", "/admin");
  });
  it("When: people tab is pressed", function() {
    cy.get(".v-btn__content > .v-icon").click();
    cy.get("[data-cy=people]").click();
  });
  it("Then: url should have /people", function() {
    cy.url().should("include", "/people");
  });
});
