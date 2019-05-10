describe("Get to Diplomas Page", () => {
  it("Given Successfull login", () => {
    cy.login();
  });

  it("When: clicking to diplomas page", () => {
    cy.deploma_page();
  });
  it("Then: should be in diplomas page", () => {
    cy.url().should("include", "/diplomas");
  });
});

describe("Flipping through Diploma Page", () => {
  it("Next Diploma Page", () => {
    cy.get('[aria-label="Siguiente página"]').click();
  });
  it("Previous Diploma Page", () => {
    cy.get('[aria-label="Pagina anterior"]').click();
  });
});

describe("Change rows per page", () => {
  it("Show 10 rows", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(2) > .v-list__tile"
    ).click();
  });
  it("Show 25 rows", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(3) > .v-list__tile"
    ).click();
  });
  it("Show all rows", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(4) > .v-list__tile"
    ).click();
  });
  it("Show 5 rows", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
  });
});

describe("Show archived/active/all diplomas", () => {
  it("Show Archived diplomas", () => {
    cy.get(
      ":nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot"
    ).click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile"
    ).click();
  });
  it("Show all diplomas", () => {
    cy.get(
      ":nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot"
    ).click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(3) > .v-list__tile"
    ).click();
  });
  it("Show Active diplomas", () => {
    cy.get(
      ":nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot"
    ).click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
  });
});

let diploma = "Above";
let non_diploma = "Testing";

describe("Search Diplomas", () => {
  it("search for existing diplomas", () => {
    cy.get("[data-cy=diplomas-table-search]").type(diploma);
    cy.get("tbody > :nth-child(1) > :nth-child(1)").contains(diploma);
  });
  it("search for non existing diplomas", () => {
    cy.get("[data-cy=diplomas-table-search]")
      .clear()
      .type(non_diploma);
    cy.get("tbody").contains("No se");
    cy.get("[data-cy=diplomas-table-search]").clear();
  });
});

describe("Open and Close Details for Diplomas", () => {
  it("Open diploma details", () => {
    cy.get("tbody > :nth-child(1) ").click();
    cy.url().should("include", "/diplomas/31");
  });
  it("Close diploma details", () => {
    cy.get(".wrap > :nth-child(1) > .v-btn").click();
  });
});

describe("Archive and Activate diploma", () => {
  it("archive diploma", () => {
    //show all diplomas
    cy.get(
      ":nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot"
    ).click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(3) > .v-list__tile"
    ).click();
    //archive above clearly million diploma
    cy.get(
      ":nth-child(1) > :nth-child(3) > .layout > :nth-child(2) > span > .v-btn"
    ).click();
    cy.get(".v-card__actions > .primary").click(); //confirm button
  });
  it("activate diploma", () => {
    cy.get(
      ":nth-child(1) > :nth-child(3) > .layout > :nth-child(2) > span > .v-btn"
    ).click();
  });
});
