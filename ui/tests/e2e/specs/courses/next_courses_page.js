describe("Flip through Courses Page", () => {
  before(() => {
    cy.login();
    cy.visit("/courses");
  });
  it("Next page", () => {
    cy.get('[aria-label="Siguiente página"]').click();
  });
  it("back page", () => {
    cy.get('[aria-label="Pagina anterior"]').click();
  });
});
