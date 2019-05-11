# Install PostgreSQL using WSL

This doc explains how to install PostgreSQL 11 on a Windows Subsystem for Linux.

If you are looking to install PostgreSQL through a Windows installer or on a Mac or Linux machine then navigate [here](https://github.com/corpus-christi/corpus-christi/blob/development/doc/develop.md#database-setup).

Credit: This tutorial has been borrowed and modified from a github repo owned by [**Michael Treat**](michaeltreat/Windows-Subsystem-For-Linux-Setup-Guide/edit/master/readmes/installs/PostgreSQL.md).

For this tutorial, we will be installing Postgres through the Ubuntu command line. You can check out the PostgreSQL Linux install docs [here](https://www.postgresql.org/download/linux/ubuntu/).

## Install
1. Open a terminal (the Ubuntu app) and then go to the root of the Ubuntu Subsystem by typing `cd ~ `.
2. Type `sudo vim ../../etc/apt/sources.list`. This will open a file on Ubuntu using the vim editor.
3. At the bottom of this file, paste in this line `deb http://apt.postgresql.org/pub/repos/apt/ <version>-pgdg main`
  - Change the last part of the line above from `<version>` to whichever version of Ubuntu you are running.
  - You can most likely find the version in the lines preceding the newly entered line. If you see something like `bionic-security`, you know your version is `bionic`.
4. When that's done, write your changes to the file and quit outt.
5. Next, copy these 2 lines and paste them into your terminal:
```
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
```
This will add postgresql 11 to your repositories so you can install the lastest version. Press `enter` when the last line pops up.

6. After the update is complete, enter in this line `sudo apt-get install postgresql-11` and press `y` when prompted.

## Postgres User Setup

postgresql-11 runs under the user `postgres`. We need to give this user a password so that postgres can allow this user to connect to the database.

1. To set the password for postgres, type `sudo passwd postgres`.
2. You will get a prompt to enter in your password. It will not show when you are typing, but it is still registering your key-strokes.
3. Close and reopen the terminal. 

## Using psql

After your first install, and each time you restart your machine you mat have to also restart the postgres service, or else you will get a `Is the server running?` error. 

1. To start the service, type `sudo service postgresql start`.
2. To connect to postgres, type `sudo -u postgres psql`. 

You should get a prompt asking for your password. If this doesn't work, then you can try the second option listed below.

1. Switch users to postgres by typing `su - postgres`.
2. Type `psql`.

When this is successful you will see the command line change to look like this `postgres=#`

## Tips / Debugging

After following this tutorial, if you still receive errors when running the `flask db upgrade` command, you may have to do some or all of the following steps. Make sure you have entered the correct information in your private.py file.

* Error: `password authentication failed`
1. You have to change the authentication method to `trust`. This makes it so no password will be requested at all when attempting to connect to the server.
2. In bash, run `sudo vim /etc/postgresql/11/main/pg_hba.conf`
3. Find the line that starts with `local all all` and replace the method with `trust` (probably from peer or md5)
4. Find the line that starts with `host all all 127.0.0.1/32` and replace the method with `trust`.
5. Write to and quit the file.
6. Restart the postgres service with `sudo service postgresql restart`

* Error: `could not flush dirty data: Function not implemented`
1. You have to turn the fsync setting in Postgres's configuration to off.
2. In bash, run `sudo vim /etc/postgresql/11/main/postgresql.conf`
3. Search for the word `fsync`
4. Uncomment the line and set it equal to off
5. Write to and quit the file.
6. Restart the postgres service with `sudo service postgresql restart`