describe("Get to Courses Page", () => {
  it("Given: Successfull login", () => {
    cy.login();
  });
  it("When: clicking to course page", () => {
    cy.course_page();
  });
  it("Then: should be in course page", () => {
    cy.url().should("include", "/courses");
  });
});

let course = "course: Energy.";

describe("Get more details on a course", () => {
  it("Click into details of course", () => {
    cy.get("tbody")
      .contains(course)
      .click();
    cy.url().should("include", "/courses/9");
  });
});

let section = "Testing";

describe("Get more section details on a course", () => {
  it("Click into details of a section", () => {
    cy.get("tbody")
      .contains(section)
      .click();
    cy.url().should("include", "/courses/9/offering/30/details");
  });
});

describe("Check Scheduled times", () => {
  it("Click schedule tab", () => {
    cy.get(":nth-child(4) > .v-tabs__item").click();
  });
  it("Add meeting time form", () => {
    cy.get(
      '[courseid="9"] > .v-toolbar > .v-toolbar__content > .v-btn'
    ).click(); //add meeting button
  });
  //Cancel button
  it("Add meeting time form - DATE Cancel button", () => {
    cy.wait(500);
    cy.get("[data-cy=course-offering-date]").click();
    cy.get(":nth-child(4) > :nth-child(5) > .v-btn").click(); //25 of Jan
    cy.get("[data-cy=course-offering-date-cancel]").click();
  });
  //Confirm button
  it("Add meeting time form - DATE Confirm button", () => {
    cy.wait(500);
    cy.get("[data-cy=course-offering-date]").click();
    cy.contains("30").click(); //30 of Jan
    cy.get("[data-cy=course-offering-date-ok]").click();
  });

  //FIGURE OUT HOW TO CLICK A CLOCK FORM
  it("Add meeting time Form - Time", () => {
    //cancel
    cy.get("[data-cy=course-offering-time]").click();
    cy.contains("1").click(); //HOUR
    cy.contains("35").click(); //Minute
    cy.get("[data-cy=course-offering-time-cancel]").click();
    //confirm
    cy.get("[data-cy=course-offering-time]").click();
    cy.contains("1").click(); //HOUR
    cy.contains("35").click(); //Minute
    cy.get("[data-cy=course-offering-time-ok]").click();
  });
  it("Add meeting form - Teacher", () => {
    cy.get("[data-cy=course-offering-teacher]").click();
    cy.contains("Scott").click();
  });
  it("Add meeting form - Location", () => {
    cy.get("[data-cy=course-offering-location]").click();
    cy.contains("Sara").click();
  });
  it("Save form", () => {
    cy.get(
      ".v-dialog__content--active > .v-dialog > .v-card > .v-card__actions > .primary"
    ).click();
    cy.get(
      ".v-toolbar__content > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot > input"
    ).type("Sara");
    //cy.get('.v-dialog__content--active > .v-dialog > .v-card > .v-card__actions > .primary').contains('Sara')
  });
});

describe("Check students in section", () => {
  it("Click into students", () => {
    cy.get(":nth-child(3) > .v-tabs__item").click();
    cy.url().should("include", "/courses/9/offering/30/students");
  });
});

// describe("Flip through students", () => {
//   it("Next student page", () => {
//     cy.get(
//       '[aria-label="Siguiente página"] > .v-btn__content > .v-icon'
//     ).click(); //next student page
//   });
//   it("flip back though student page", () => {
//     cy.get(
//       '[aria-label="Pagina anterior"] > .v-btn__content > .v-icon'
//     ).click(); //back student page
//   });
// });

describe("Number of students on page", () => {
  it("show 15", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click(); //drop down arrow
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(2) > .v-list__tile"
    ).click();
  });
  it("show 25", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(3) > .v-list__tile"
    ).click();
  });
  it("show all", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(4) > .v-list__tile"
    ).click();
  });
  it("show 10", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    );
  });
});

describe("Get back to course details", () => {
  it("Click back to course details", () => {
    cy.get('.container > [data-v-6bac62c4=""] > :nth-child(1)').click(); //back button
    cy.url().should("include", "/courses/9");
  });
});

describe("Search for course section", () => {
  it("section box", () => {
    cy.get(
      ".layout > .flex > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot > input"
    ).type("Test");
  });
  it("should find match", () => {
    cy.get("tbody > tr > :nth-child(1)").contains("Testing");
  });
  it("clears search bar", () => {
    cy.get(
      ".layout > .flex > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot > input"
    ).clear();
  });
});

describe("Active/Archived/All Sections", () => {
  it("List of archived sections", () => {
    cy.get(".v-text-field--solo > .v-input__control > .v-input__slot").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile"
    ).click();
  });
  it("List of all sections", () => {
    cy.get(".v-text-field--solo > .v-input__control > .v-input__slot").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(3) > .v-list__tile"
    ).click();
  });
  it("List of active sections", () => {
    cy.get(".v-text-field--solo > .v-input__control > .v-input__slot").click();

    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
  });
});

describe("Get back to courses page", () => {
  it("Click back to courses page", () => {
    cy.get(".xs12 > .v-btn").click(); //back button
    cy.url().should("include", "/courses");
  });
});
