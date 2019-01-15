//Log in
describe("Seed for test", function() {
  it("Given: seeding", function() {
    cy.exec("cd ../api && source ./set-up-bash.sh && ./reset-database.sh");
  });
});

describe("Getting to the people page", function() {
  it("Given: logs in successfully", function() {
    cy.visit("/login");
    cy.get("[data-cy=username]").type("Cytest");
    cy.get("[data-cy=password]").type("password");
    cy.get("[data-cy=login]").click();
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

describe("testing the change view dropdown on the person table", () => {
  it("Given: dropdown opens", function() {
    cy.get(
      ".layout > :nth-child(3) > .v-input > .v-input__control > .v-input__slot"
    ).click();
  });
});
