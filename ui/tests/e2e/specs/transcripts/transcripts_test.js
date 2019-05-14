// TODO: Needs to be split up into multiple tests

describe("Get to Transcripts Page", () => {
	it("GIVEN Successful login", () => {
		cy.login();
	});

	it("WHEN: Navigating to transcripts page", () => {
		cy.get("[data-cy=toggle-nav-drawer]").click();
		cy.get(".v-list__group__header__append-icon").click();
		cy.get("[data-cy=transcripts]").click();
	});
	it("THEN: Should be at transcripts page", () => {
		cy.url().should("include", "/transcripts");
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

describe("Add Diploma to student", () => {
	it("Student transcript details", () => {
		cy.get("tbody").eq(0).click();
		cy.get("[data-cy=student-details]");
		cy.get("[data-cy=add-diploma-this-student]").click();
		cy.wait(350);
		cy.get(".v-input__slot").click();
		cy.get(":nth-child(1) > .v-list__tile > .v-list__tile__content").click();
		cy.get("[data-cy=save]").click();
		cy.get("[data-cy=back-button]").click();
	});
});