export default class Account {
  constructor(username, firstName, lastName) {
    this.username = username;
    this.firstName = firstName;
    this.lastName = lastName;
  }

  fullName() {
    return `${this.firstName} ${this.lastName}`;
  }
}
