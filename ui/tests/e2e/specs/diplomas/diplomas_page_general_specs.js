describe("Diplomas Page General Testing", () => { // Tests button funcitonality 
  it("GIVEN: Successfull login", () => {
    cy.login();
  });

  it("WHEN: clicking to diplomas page", () => {
    cy.deploma_page()
  });
  it("THEN: should be in diplomas page", () => {
    cy.url().should("include", "/diplomas");
  });
});

// Tough to apply GivenWhenThen methodology here as it 
//     tests individual pieces of the diplomas page. 

describe("Flipping through Diploma Page", () => {
  it("Next Diploma Page", () => {
    cy.get('[aria-label="Siguiente página"]').click()
  });
  it("Previous Diploma Page", () => {
    cy.get('[aria-label="Pagina anterior"]').click()
  });
});

describe('Change rows per page', () =>{
  it('Show 10 rows', () => {
    cy.get('.v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
    cy.get('.v-menu__content--auto > .v-select-list > .v-list > :nth-child(2) > .v-list__tile').click()
  })
  it('Show 25 rows', () => {
    cy.get('.v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
    cy.get('.v-menu__content--auto > .v-select-list > .v-list > :nth-child(3) > .v-list__tile').click()
  })
  it('Show all rows', () => {
    cy.get('.v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
    cy.get('.v-menu__content--auto > .v-select-list > .v-list > :nth-child(4) > .v-list__tile').click()
  })
  it('Show 5 rows', () => {
    cy.get('.v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
    cy.get('.v-menu__content--auto > .v-select-list > .v-list > :nth-child(1) > .v-list__tile').click()
  })
})

describe("Show archived/active/all diplomas", () => {
  it("Archived diplomas", () => {
    cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').click()
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile').click()
  });
  it("Show all diplomas", () => {
    cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').click()
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(3) > .v-list__tile').click()
  });
  it("Show Active diplomas", () => {
    cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot').click()
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile').click()
  });
});

describe("Open and Close Diplomas Details", () => {
  it("Open diploma details", () => { // Opens one deploma for an expanded view
    cy.get('tbody > :nth-child(1) ').click()
    cy.url().should("include", "/diplomas/");

  });
  it('Close diploma details', () => {
    cy.get("[data-cy=arrow_back_button]").click() // Button to go back to view all diplomas
  })
});


