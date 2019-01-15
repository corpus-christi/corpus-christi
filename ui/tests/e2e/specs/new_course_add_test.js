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

// describe('Add Course', ()=>{
//     it('Given: New Course Form', () =>{
//         cy.get('.shrink > .v-btn').click()
//     });
//     it('When: Form is filled out', ()=>{
//         cy.get('[aria-required="true"] > .v-input__control > .v-input__slot > .v-text-field__slot > input').type('COS 5')
//         cy.get('textarea').type('Hello World')
//     });
//     it('Then: Click add button', ()=>{
//         cy.get('.v-dialog__content--active > .v-dialog > .v-card > .v-card__actions > .primary').click()
//         cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
//         cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(3) > .v-list__tile').click
//     });
// });
