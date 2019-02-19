describe("Testing Editing User Information", () => {
  it(
    "Given: Visits the app root url, logs into an account, navigates" +
      "to the people page, and filters the search to one person",
    () => {
      cy.login();
      //Making sure we're in the right place
      cy.url().should("include", "/admin");
      //open nav drawer
      cy.get("[data-cy=toggle-nav-drawer]").click();
      //goes to the people page
      cy.get("[data-cy=people]").click();
      cy.get("[data-cy=search]").type("Quality");
    }
  );
  it("When: Clicking on the gear button", () => {
    cy.get("[data-cy=person-table]").within(() => {
      cy.get("[data-cy=account-settings]").click();
    });
  });
  it("Then: The person's password can be changed", () => {
    cy.get(".v-dialog__content--active > .v-dialog > .v-card").within(() => {
      cy.get("[data-cy=new-update-password]").type("foobar123");
      cy.get("[data-cy=confirm-password]").type("foobar123");
      cy.get("[data-cy=confirm-button]").click();
    });
  });

  it("And: The new password can be used to log the user in", () => {
    cy.get("[data-cy=account-menu]").click();
    cy.get("[data-cy=logout]").click();
    cy.get("[data-cy=account-button]").click();
    cy.get("[data-cy=username]").type("Cytest");
    cy.get("[data-cy=password]").type("foobar123");
    cy.get("[data-cy=login]").click();
    cy.url().should("include", "/admin");
  });
  it(
    "Finally: The password can be changed as many times as desired, so long as the password is 8+ characters, and " +
      "the two fields match",
    () => {
      cy.get("[data-cy=toggle-nav-drawer]").click();
      cy.get("[data-cy=people]").click();
      cy.get("[data-cy=search]").type("Quality");
      cy.get("[data-cy=person-table").within(() => {
        cy.get("[data-cy=account-settings]").click();
      });
      cy.get(".v-dialog__content--active > .v-dialog > .v-card").within(() => {
        cy.get("[data-cy=new-update-password]").type("test");
        cy.get(
          ":nth-child(1) > .v-input__control > .v-text-field__details"
        ).should("not.be.empty");
        cy.get("[data-cy=confirm-password]").type("bad");
        cy.get(
          ":nth-child(2) > .v-input__control > .v-text-field__details "
        ).should("not.be.empty");
        cy.get("[data-cy=new-update-password]")
          .clear()
          .type("password");
        cy.get("[data-cy=confirm-password]")
          .clear()
          .type("password");
        cy.get("[data-cy=confirm-button]").click();
      });
    }
  );
  it("Also: The cancel button brings the user out of the text field", () => {
    cy.get("[data-cy=person-table]").within(() => {
      cy.get("[data-cy=account-settings]").click();
    });
    cy.get(".v-dialog__content--active > .v-dialog > .v-card").within(() => {
      cy.get("[data-cy=cancel-button]").click();
      cy.get(".v-dialog__content--active > .v-dialog").should("not.exist");
    });
  });
});
