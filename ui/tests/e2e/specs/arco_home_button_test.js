//Cicking Arco logo while on home page
describe("Click Arco from home page", function() {
  it("Given: successfully loads", function() {
    cy.visit("/");
  });
  it("When: clicks arco home button", () => {
    cy.get("[data-cy=home-logo] > img").click();
  });
  it("Then: checks url", () => {
    cy.url().should("include", "/public");
  });
});

//Clicking Arco logo while on login page
describe("Click Arco from login page", function() {
  it("Given: loads login page successfully", function() {
    cy.visit("/login");
  });
  it("When: clicks arco home button", () => {
    cy.get("[data-cy=home-logo] > img").click();
  });
  it("Then: checks url", () => {
    cy.url().should("include", "/public");
  });
});
