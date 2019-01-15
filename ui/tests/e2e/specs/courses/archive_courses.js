// describe("Get to Courses Page", () => {
//     it("Given Successfull login", () => {
//       cy.visit("/");
//       cy.get("[data-cy=account-button]").click();
//       cy.get("[data-cy=username]").type("lpratico");
//       cy.get("[data-cy=password]").type("Qwerty1234");
//       cy.get("[data-cy=login]").click();
//     });
  
//     it("When: clicking to course page", () => {
//       cy.get("[data-cy=open-navigation]").click();
//       cy.get(":nth-child(5) > .v-list__tile").click();
//     });
//     it("Then: should be in course page", () => {
//       cy.url().should("include", "/courses");
//     });
// });

describe('The Dashboard Page', function () {
    beforeEach(function () {
      // reset and seed the database prior to every test
      cy.exec(npm run db:reset && npm run db:seed')
  
      // seed a user in the DB that we can control from our tests
      // assuming it generates a random password for us
      cy.request('POST', '/test/seed/user', { username: 'lpratico' })
        .its('body')
        .as('currentUser')
    })
  
    it('logs in programmatically without using the UI', function () {
      // destructuring assignment of the this.currentUser object
      const { username, password } = this.currentUser
  
      // programmatically log us in without needing the UI
      cy.request('POST', '/login', {
        username,
        password
      })
  
      // now that we're logged in, we can visit
      // any kind of restricted route!
      cy.visit('/courses')
  
      // our auth cookie should be present
      cy.getCookie('your-session-cookie').should('exist')
  
      // UI should reflect this user being logged in
      cy.get('h1').should('contain', 'Lily Pratico')
    })
})

// describe("archive courses", () => {
//     it("click archive button", () => {
//         cy.get(':nth-child(1) > :nth-child(3) > .layout > :nth-child(2) > span > .v-btn').click()
//         cy.get('.v-dialog__content--active > .v-dialog > .v-card > .v-card__actions > .primary').click()
//     });
//     it("check archive course", () => {
//         cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
//     });
// });

