# 507_Final-Project
To run this program, you need to do the following things:
1) get client key and client secret. You can apply for authentication from Yelp API  using the link below.
     "https://www.yelp.com/developers/v3/manage_app"
   Or you can get them from canvas submission
   insert such values into the file 'SI507F17_finalproject.py' which asks for client and client secret.
2) create a database called "foodieguide"
3) change username to your account name on your computer in line 28  in'SI507F17_finalproject.py'
4) use python3 to run 'SI507F17_finalproject.py'
5) install requirement in requirements.txt file
6) type any food you would like to search, such as "sushi","seafood", 'burger','hotpot' at command prompt

7）type the city name where you would like to have this food such as 'chicago', 'ann arbor' at command prompt

Yelp API would give you a list of restaurants which meet your search requirements. A CSV file will display following information for up to 50 restaurants found in the location that you chose
  -restaurant name
  -Rating
  -Review_number(e.g. how many people have given reviews)
  -Distance (miles)
  -Phone
  -Address
  -Category (what type of food they are serving)
  -Transactions (e.g. delivery)
  -Price_range (e.g. $, $$,$$$)

You can open a CSV file called "Restaurants" to see a bunch of restaurants which provide food of your interest
Type the restaurant of your interest
You will see the restaurant's operation hours in plotly graph with trace 1 representing opening hours and trace 2 representing closing hours
*also you can use command psql foodieguide to check database in TeamSQL
