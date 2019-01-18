describe("Get to Courses Page", () => {
    it("Given Successfull login", () => {
      cy.login()
    });
  
    it("When: clicking to course page", () => {
        cy.get('[data-cy=toggle-nav-drawer]').click();
        cy.get('[data-cy=courses-admin]').click();
    });
    it("Then: should be in course page", () => {
        cy.url().should("include", "/courses");
    });
});


describe("Archive Courses", () => {
    it("click archive button", () => {
        cy.get('[data-cy=courses-table-search]').type('Debate until.')
        //cy.contains('Debate until.').click()
        cy.get(':nth-child(2) > span > .v-btn').click()//click archive
        cy.get('.v-dialog__content--active > .v-dialog > .v-card > .v-card__actions > .primary').click()//confirm click
    });
    it("check archive course", () => {
        cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
        cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile').click()
        cy.get('tbody').contains('Debate')
    });
});

describe('Activate archive courses', () => {
    it('click activate button', () =>{
        cy.get(':nth-child(2) > span > .v-btn').click()
    });
    it('Get back to active courses', () => {
        cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
        cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile').click()
        cy.get('tbody').contains('Debate')
    });
});

