//So, here's the deal with this test
//It was working at one point, and then the UI changed.
//For reference on how to get it working again, it is very similar to how add_person works
//But I currently do not have the time to finish this.
describe("Admin edits user information", function() {
  it("Given: logs in, navigates to people page", function() {
    cy.login();
    cy.get("[data-cy=toggle-nav-drawer]").click();
    cy.get("[data-cy=people]").click();
    cy.url().should("include", "/people");
  });
  it("When: The edit information button is pressed:", function() {
    cy.get("[data-cy=search]").type("Quality");
    cy.get("[data-cy=person-table]").within(() => {
      cy.get("tbody > :nth-child(1) > :nth-child(2)")
        .invoke("text")
        .as("firstName");
      cy.get("tbody > :nth-child(1) > :nth-child(3)")
        .invoke("text")
        .as("lastName");
      cy.get("tbody > :nth-child(1) > :nth-child(4)")
        .invoke("text")
        .as("email");
      cy.get("tbody > :nth-child(1) > :nth-child(5)")
        .invoke("text")
        .as("phone");
      cy.get("[data-cy=edit-person]").click();
    });
  });
  it("Then: The information showing on the form should be the same as what was showing on the table", function() {
    cy.get("[data-cy=first-name]").should("have.value", this.firstName);
    cy.get("[data-cy=last-name]").should("have.value", this.lastName);
    cy.get("[data-cy=email]").should("have.value", this.email);
    cy.get("[data-cy=phone]").should("have.value", this.phone);
  });

  it("And: The information should be mutable", function() {
    cy.get("[data-cy=first-name]")
      .clear()
      .type("TESTME");
    cy.get("[data-cy=last-name]")
      .clear()
      .type("LASTNAME");
    cy.get("[data-cy=show-birthday-picker]").click(); //open birthday picker
    cy.get(":nth-child(3) > :nth-child(5) > .v-btn > .v-btn__content").click(); //select birthday
    cy.get("[data-cy=email]")
      .clear()
      .type("editMe@gmail.com"); //email
    cy.get("[data-cy=phone]")
      .clear()
      .type("123-456-7890"); //phone
    cy.get("[data-cy=radio-gender]").within(() => {
      cy.get(".v-label")
        .first()
        .click(); //Male
    });
    /*cy.get('[data-cy=save]').click();
    cy.get('[data-cy=search]').clear().type("TESTME");
    cy.get("[data-cy=person-table").within(() => {
    cy.get('tbody > :nth-child(1) > :nth-child(2)').should('contain', 'TESTME');
    cy.get('tbody > :nth-child(1) > :nth-child(3)').should('contain', 'LASTNAME');
    cy.get('tbody > :nth-child(1) > :nth-child(4)').should('contain', 'editMe@gmail.com');
    cy.get('tbody > :nth-child(1) > :nth-child(5)').should('contain', '123-456-7890');*/
    cy.get("[data-cy=save]").click();
    cy.get("[data-cy=search]")
      .clear()
      .type("TESTME");
    cy.get("[data-cy=person-table").within(() => {
      cy.get("tbody > :nth-child(1) > :nth-child(2)").should(
        "contain",
        "TESTME"
      );
      cy.get("tbody > :nth-child(1) > :nth-child(3)").should(
        "contain",
        "LASTNAME"
      );
      cy.get("tbody > :nth-child(1) > :nth-child(4)").should(
        "contain",
        "editMe@gmail.com"
      );
      cy.get("tbody > :nth-child(1) > :nth-child(5)").should(
        "contain",
        "123-456-7890"
      );
      cy.get("[data-cy=edit-person]").click();
    });
    cy.get("[data-cy=first-name]")
      .clear()
      .type("Quality");
    cy.get("[data-cy=last-name]")
      .clear()
      .type("Assurance");
    cy.get("[data-cy=save]").click();
    cy.get("[data-cy=search]")
      .clear()
      .type("Quality");
  });
  it("And: Ensure form fields work as they should", () => {
    //cy.get("[data-cy=edit-person]").click();
    //Making sure that name fields do not allow numbers
    //waiting on this to actually be implemented by UI
    //Making sure that the phone field does not allow letters & has a length limit
    //waiting on this to actually be implemented by UI
    //Make sure you cannot select a date in the future
    //waiting on this to actually be implemented by UI
    //cy.get('.v-date-picker-header > :nth-child(3)').click();
    //cy.contains('17').click();
    //Make sure the email is valid
    cy.get("[data-cy=email]")
      .clear()
      .type("NotARealEmail");
    cy.get("[data-cy=save]").click();
    cy.get(
      ":nth-child(6) > .v-input__control > .v-text-field__details"
    ).contains("válido");
    cy.get("[data-cy=email]")
      .clear()
      .type("testEmail@aol.com");
    cy.get("[data-cy=save]").click();
    cy.get(":nth-child(6) > .v-input__control > .v-text-field__details").should(
      "not.contain",
      "válido"
    );
  });
  it("And: Ensure the form is filled out with enough information before save/add another can proceed", () => {
    cy.get("[data-cy = save]").click();
    cy.get(
      ":nth-child(1) > .v-input__control > .v-text-field__details"
    ).contains("obligatorio");
    cy.get(
      ":nth-child(2) > .v-input__control > .v-text-field__details"
    ).contains("obligatorio");
    cy.get("[data-cy=first-name]").type("Test"); //first name
    cy.get("[data-cy=last-name]").type("Me"); //last name
    //cy.get('[data-cy=save]').click();
    //cy.get('[data-cy=search]').clear().type("Test");
    //cy.get("[data-cy=first-name]").should("be.empty");
    //cy.get('[data-cy=last-name]').should("be.empty");
  });
  it("Finally: The cancel button should exit the form", function() {
    cy.get("[data-cy=cancel").click();
    cy.get(".v-dialog__content--active > .v-dialog").should("not.exist");
  });
});
