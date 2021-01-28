 /**
 * Prefix in the I18N database for roles.
 * @type {string}
 */
const ROLE_PREFIX = "role.";

/**
 * Name of the superuser role.
 * @type {string}
 */
const ROLE_SUPERUSER = `${ROLE_PREFIX}superuser`;

export default class Account {
  constructor(username, firstName, lastName, roles, id, email = null) {
    this.username = username;
    this.firstName = firstName;
    this.lastName = lastName;
    this.roles = roles;
    this.id = id;
    this.email = email;
  }

  fullName() {
    return `${this.firstName} ${this.lastName}`;
  }

  /**
   * Does this user have superuser permissions?
   */
  isSuperuser() {
    this.roles.find((elt) => elt === ROLE_SUPERUSER);
  }

  /**
   * Does this user have role `role`?
   * If the user is the superuser, the answer is always "yes."
   * @param role - name of role, not including the ROLE_PREFIX
   * @returns boolean
   */
  hasRole(role) {
    return (
      this.isSuperuser() ||
      this.roles.find((elt) => elt === `${ROLE_PREFIX}${role}`)
    );
  }

  /**
   * Used to convert ordinary object to a class object
   * after restoring them from localstorage
   */
  static fromObject(obj) {
    return Object.assign(new Account(), {
      username: obj.username,
      firstName: obj.firstName,
      lastName: obj.lastName,
      roles: obj.roles,
      id: obj.id,
      email: obj.email,
    });
  }
}
