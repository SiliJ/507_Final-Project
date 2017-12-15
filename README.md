# 507_Final-Project
To run this program, you need to do the following things:
1) get client key and client secret. You can apply for authentication from Yelp API  using the link below. Or you can get them from canvas submission
     "https://www.yelp.com/developers/v3/manage_app"
2) create a database called "foodieguide"
3) change username to your account name on your computer in line 28
4) use python3
5) install requirement in requirements.txt file
6) type any food you would like to search, such as "sushi","seafood", 'burger' at command prompt
7）type the city name where you would like to have this food such as 'chicago', 'ann arbor' at command prompt

Yelp API would give you a table which includes all the relevant restaurants it the location that you chose with the info below:
  restaurant name
  restaurant ID
  Rating
  Review_count
  Distance
  Phone
  Address
  Category (what type of food they are serving)
  Transactions (e.g. delivery)
  Price_range (e.g. $, $$,$$$)

You can click on the restaurant ID of your interest and get a table of its operation hours over the week.
use command psql foodieguide to check database in TeamSQL
