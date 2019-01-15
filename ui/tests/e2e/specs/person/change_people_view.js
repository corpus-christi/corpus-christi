// Log in
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
    cy.get("[data-cy=toggle-nav-drawer]").click();
    cy.get("[data-cy=people]").click();
  });
  it("Then: url should have /people", function() {
    cy.url().should("include", "/people");
  });
});

describe("testing the change view dropdown on the person table", () => {
  it("Given: dropdown opens", function() {
    cy.get("[data-cy=view-dropdown]").click(); // open dropdown
  });
  it("When: admin views archived users", function() {
    let dropdown = ".menuable__content__active > .v-select-list > .v-list"; // path to dropdown child elements
    // Important: Don't re-select default value first
    // View Archived Users
    cy.get(dropdown)
      .find(":nth-child(2)")
      .first()
      .click(); // find and click child element in dropdown
  });
  it("Then: no archived users in the table", function() {
    cy.get("tbody")
      .find("tr")
      .should("have.length", 1); // One row: no data
  });
});
