// NOTE: Test will fail if there are no members on a team
function getAllTeamsOnPage() {
  cy.get(
    ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
  ).click();
  cy.get(
    ":nth-child(4) > .v-list__tile > .v-list__tile__content > .v-list__tile__title"
  ).click();
  cy.get(".md3 > .v-input > .v-input__control > .v-input__slot").click();
  cy.get(
    ".menuable__content__active > .v-select-list > .v-list > :nth-child(3) > .v-list__tile > .v-list__tile__content"
  ).click();
}

describe("Check Team Members Test", () => {
  before(() => {
    cy.login();
  });

  it("GIVEN: User goes to the listing of all teams", () => {
    cy.visit("/teams");
    getAllTeamsOnPage();
    cy.wait(500);
  });

  it("THEN: The member information and team description are listed when each team is accessed", () => {
    var i = 1;
    cy.get(".container").then(container => {
      while (container.find(":nth-child(" + i + ") > .hover-hand").length) {
        cy.log(container.find(":nth-child(" + i + ") > .hover-hand").length);
        cy.get(":nth-child(" + i + ") > .hover-hand").click();
        cy.get(
          ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
        ).click();
        cy.get(
          ":nth-child(4) > .v-list__tile > .v-list__tile__content > .v-list__tile__title"
        ).click();
        cy.wait(1000);
        cy.get(".v-btn--router > .v-btn__content").click();
        getAllTeamsOnPage();
        i += 1;
      }
    });
  });
});
