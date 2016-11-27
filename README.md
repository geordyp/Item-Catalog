## Item_Catalog
The goal for this project was to create a web application that
provides a list of items within a variety of categories and
integrates third party user registration and authentication.
For the latter, I used oauth to integrate Google sign in.

I named the web application "Yo Check This Out!" The concept
for the site is users can log in and share recommendations
they have for other users to check out. The categories listed
include movies, games, and music. Users are able to add
recommendations under those categories sharing their favorite
items in each category.

## Setup
1. Fork the [fullstack-nanodegree-vm repo](https://github.com/udacity/fullstack-nanodegree-vm) and clone to your machine.
2. cd into /vagrant/catalog and replace its contents with
   this repo's code
3. From the catalog directory use the command 'vagrant up'
   followed by 'vagrant ssh'
4. Once vagrant is up and running cd to into /vagrant/
5. The database should be setup already. Incase you want to
   start fresh, you can delete catalog.db and use the
   'python database_setup.py' command. Then use the
   'python populate_database.py' command to add the
   categories and some filler data. I make it clear in
   the file where unnecessary data is added so feel free
   to remove or comment out those lines if you wish.
6. At this point, all the data should be setup. You can launch
   the application using the 'python application.py' command.
   Just open up a browser and navigate to localhost:5000.
