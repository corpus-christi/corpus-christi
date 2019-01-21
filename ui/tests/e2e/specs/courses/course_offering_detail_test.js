describe("Get to Courses Page", () => {
    it("Given: Successfull login", () => {
      cy.login()
    });
    it("When: clicking to course page", () => {
      cy.course_page()
    });
    it("Then: should be in course page", () => {
      cy.url().should("include", "/courses");
    });
});

let course = 'Alone low investment'

describe('Get more details on a course', () =>{
  it('Click into details of course', () =>{
    cy.get('tbody').contains(course).click()
    cy.url().should("include", "/courses/1");
  })
})

let section = 'Around happy fast'

describe('Get more section details on a course', () =>{
  it('Click into details of a section', () =>{
    cy.get('tbody').contains(section).click()
    cy.url().should("include", "/courses/1/offering/5/details");
  })
})

describe('Check students in section', () =>{
  it('Click into students', () =>{
    cy.get(':nth-child(3) > .v-tabs__item').click()
    cy.url().should("include", "/courses/1/offering/5/students");
  })
})

describe('Flip through students', () =>{
  it('Next student page', () =>{
    cy.get('[aria-label="Siguiente página"] > .v-btn__content > .v-icon').click()//next student page
  })
  it('flip back though student page', () => {
    cy.get('[aria-label="Pagina anterior"] > .v-btn__content > .v-icon').click()//back student page
  })
})

describe('Number of students on page', () =>{
  it('show 10', () =>{
    cy.get('.v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()//drop down arrow
    cy.get('.v-select-list > .v-list > :nth-child(2)').click()
  })
  it('show 25', () => {
    cy.get('.v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
    cy.get('.v-select-list > .v-list > :nth-child(3)').click()
  })
  it('show all', () => {
    cy.get('.v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
    cy.get('.v-select-list > .v-list > :nth-child(4)').click()
  })
  it('show 5', () => {
    cy.get('.v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
    cy.get('.v-select-list > .v-list > :nth-child(1)').click()
  })
})

describe('Get back to course details', () =>{
  it('Click back to course details', () =>{
    cy.get('.v-btn--outline').click()//back button
    cy.url().should("include", "/courses/1");
  })
})

describe('Search for course section', () =>{
  it('section box', () =>{
    cy.get(':nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot > input').type('Around')
  })
  it('should find match', () =>{
    cy.get('tbody > tr > :nth-child(1)').contains("Around");
  })
  it('clears search bar', () => {
    cy.get(':nth-child(3) > .v-input > .v-input__control > .v-input__slot > .v-text-field__slot > input').clear()
  })
})

describe('Active/Archived/All Sections', () =>{
  it('List of archived sections', () =>{
    cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile').click()
  })
  it('List of all sections', () =>{
    cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(3) > .v-list__tile').click()
  })
  it('List of active sections', () =>{
    cy.get(':nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon').click()
    cy.get('.menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile').click()
  })
})

describe('Get back to courses page', () =>{
  it('Click back to courses page', () =>{
    cy.get('.xs12 > .v-btn').click()//back button
    cy.url().should("include", "/courses");
  })
})

