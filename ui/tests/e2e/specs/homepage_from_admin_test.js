//Tests logging into account and then clicking homepage
describe("Clicking home after logging in", function() {
  it("Given: logs in successfully", function() {
    cy.visit("/login");
    cy.get("[data-cy=username]").type("Cytest");
    cy.get("[data-cy=password]").type("password");
    cy.get("[data-cy=login]").click();
    cy.url().should("include", "/admin");
  });
  it("When: homebutton is pressed", function() {
    cy.get(".v-btn__content > .v-icon").click();
    cy.get(
      ".v-navigation-drawer > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
  });
  it("Then: url should have /public", function() {
    cy.url().should("include", "/public");
  });
});

//Tests click person and checking that they are still logged in
describe("Clicking person and still logged it", function() {
  it("Given: on homepage after login", function() {
    cy.url().should("include", "/public");
  });
  it("When: person bubble is clicked", function() {
    cy.get(".v-btn__content > .v-icon").click();
  });
  it("Then: url should be admin", function() {
    cy.url().should("include", "/admin");
  });
});
