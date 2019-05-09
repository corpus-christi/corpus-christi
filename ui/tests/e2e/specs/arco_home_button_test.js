//Cicking Arco logo while on home page
describe("Click Arco from home page", function() {
  it("GIVEN: Home Page", function() {
    cy.visit("/");
  });
  it("WHEN: clicks arco home button", () => {
    cy.get("[data-cy=home-logo] > img").click();
  });
  it("THEN: Check url", () => {
    cy.url().should("eq", "http://localhost:8080/");
  });
});

//Clicking Arco logo while on login page
describe("Click Arco from login page", function() {
  it("GIVEN: Login Page", function() {
    cy.visit("/login");
  });
  it("WHEN: Clicking arco home button", () => {
    cy.get("[data-cy=home-logo] > img").click();
  });
  it("THEN: Check Url", () => {
    cy.url().should("eq", "http://localhost:8080/");
  });
});
