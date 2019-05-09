describe("Test the language button", () => {
  it("GIVEN: Home Page", () => {
    cy.visit("/");
  });
  it("WHEN: Switching the language", () => {
    cy.get("[data-cy=cur-locale]").click();
    cy.get("[data-cy=en-US]").click();
  });
  it("THEN: Check for English", () => {
    cy.get("[data-cy=church-sentence]").contains("Church");
  });
  it("AND: Switch the language back to Spanish", () => {
    cy.get("[data-cy=cur-locale]").click();
    cy.get("[data-cy=es-EC]").click();
  });
  it("AND: Check for Spanish", () => {
    cy.get("[data-cy=church-sentence]").contains("Iglesia");
  });
});
