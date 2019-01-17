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


describe("archive courses", () => {
    it("click archive button", () => {
        cy.get(':nth-child(4) > :nth-child(3) > .layout > :nth-child(2) > span > .v-btn').click()
        cy.get('.v-dialog__content--active > .v-dialog > .v-card > .v-card__actions > .primary').click()
    });
    it("check archive course", () => {
        cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
        cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile').click()
        cy.get('tbody > :nth-child(5) > :nth-child(1)').contains("Identify.")
    });
});

describe('Activate archive courses', () => {
    it('click activate button', () =>{
        cy.get(':nth-child(5) > :nth-child(3) > .layout > :nth-child(2) > span > .v-btn').click()
    });
    it('Get back to active courses', () => {
        cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
        cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile').click()
    });
});

