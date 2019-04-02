describe("Get to Transcripts Page", () => {
  it("Given Successfull login", () => {
    cy.login();
  });

  it("When: clicking to diplomas page", () => {
    cy.transcript_page();
  });
  it("Then: should be in diplomas page", () => {
    cy.url().should("include", "/transcripts");
  });
});

describe("Fill through student page", () => {
  it("Next page", () => {
    cy.get('[aria-label="Siguiente página"]').click();
    cy.get('[aria-label="Siguiente página"]').click();
  });
  it("Previous page", () => {
    cy.get('[aria-label="Pagina anterior"]').click();
    cy.get('[aria-label="Pagina anterior"]').click();
  });
});

describe("Number of students shown", () => {
  it("Show 10 students", () => {
    cy.get(".v-select__slot").click();
    cy.get(".v-select-list > .v-list > :nth-child(2) > .v-list__tile").click();
  });
  it("Show 25 students", () => {
    cy.get(".v-select__slot").click();
    cy.get(".v-select-list > .v-list > :nth-child(3) > .v-list__tile").click();
  });
  it("Show All students", () => {
    cy.get(".v-select__slot").click();
    cy.get(".v-select-list > .v-list > :nth-child(4) > .v-list__tile").click();
  });
  it("Show 5 students", () => {
    cy.get(".v-select__slot").click();
    cy.get(".v-select-list > .v-list > :nth-child(1) > .v-list__tile").click();
  });
});

let student = "Fisher";

describe("Search for students", () => {
  it("search for student", () => {
    cy.get("[data-cy=transcripts-table-search]").type(student);
    cy.get("tbody > :nth-child(1) > :nth-child(1)").contains(student);
  });
});

describe("Transcript for student", () => {
  it("Student transcript details", () => {
    cy.get("tbody > :nth-child(1) > :nth-child(1)").click();
    cy.url().should("include", "/transcripts/3");
    cy.wait(500);
  });
});

describe("Add diploma to student", () => {
  it("add diploma to student form", () => {
    cy.get("[data-cy=add-diploma-this-student]").click();
    cy.get(".v-input__slot").click();
    cy.get(".v-card__actions > .v-btn--flat").click(); //cancel
  });
});

describe("Back button", () => {
  it("Go back to all students", () => {
    cy.get(".row > :nth-child(1) > .v-btn").click();
    cy.url().should("include", "/transcripts/all");
  });
});
