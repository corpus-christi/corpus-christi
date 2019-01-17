describe("Get to Courses Page", () => {
    it("Given Successfull login", () => {
      cy.visit("/");
      cy.get("[data-cy=account-button]").click();
      cy.get("[data-cy=username]").type("lpratico");
      cy.get("[data-cy=password]").type("Qwerty1234");
      cy.get("[data-cy=login]").click();
    });
  
    it("When: clicking to course page", () => {
      cy.get("[data-cy=open-navigation]").click();
      cy.get(":nth-child(5) > .v-list__tile").click();
    });
    it("Then: should be in course page", () => {
      cy.url().should("include", "/courses");
    });
});

describe("Edit courses", () => {
    it("Open edit course", () => {
        cy.get(':nth-child(1) > :nth-child(3) > .layout > :nth-child(1) > span > .v-btn').click()
    });
    it("change course title", () => {
        cy.get('[data-cy=course-form-name]').clear().type("Alone low investment")
    });
    it('save changes', () => {
        cy.get('[data-cy=course-editor-actions] > .primary').click()
    });
});