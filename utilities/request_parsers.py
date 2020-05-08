
'''
There was too much clutter in the resources files, so I pulled out defining of requests parsers.
'''

from flask_restful import reqparse

#create parser for incoming user data
u_parser = reqparse.RequestParser()
u_parser.add_argument('username', help = 'Username cannot be blank.', required = True)
u_parser.add_argument('email', help = 'Please include a valid email address.', required = True)
u_parser.add_argument('password', help = 'Please enter a valid password.', required = True)
u_parser.add_argument('age', help = 'Please enter an age.', required = True)
u_parser.add_argument('gender_identity', help = 'Please enter an age.', required = True)
u_parser.add_argument('activity_level', help = 'We need your activity level for nutritious recommendations.', required = True)

#create parser for incoming geolocal data
r_parser = reqparse.RequestParser()
r_parser.add_argument('latitude', help= 'Latitude parameter is required.', required = True)
r_parser.add_argument('longitude', help= 'Longitude parameter is required.', required = True)
r_parser.add_argument('distance', help= 'Distance parameter is required.', required = True)

#Preference parser
p_parser = reqparse.RequestParser()
p_parser.add_argument('preference', help = 'This field cannot be blank', required = True)
p_parser.add_argument('preference_action', help = 'This field cannot be blank', required = True)

#Admin parser
a_parser = reqparse.RequestParser()
a_parser.add_argument('action', help = 'This field cannot be blank', required = False)
a_parser.add_argument('new_admin', help = 'This field only needs to be filled when adding new admin.', required = False)
a_parser.add_argument('item_name', help = 'This field needs to be added when updating food table', required = False)
a_parser.add_argument('latitude', help = 'This field needs to be added when updating food table', required = False)
a_parser.add_argument('longitude', help = 'This field needs to be added when updating food table', required = False)

#email link parser
e_parser = reqparse.RequestParser()
e_parser.add_argument('token', help = 'include the token.', required = True)

#food link parser
f_parser = reqparse.RequestParser()
f_parser.add_argument('item_name', help = 'include the token.', required = True)
f_parser.add_argument('latitude', help = 'include the latitude.', required = True)
f_parser.add_argument('longitude', help = 'include the longitude.', required = True)
f_parser.add_argument('restaurant_name', help = 'include the restaurant name.', required = True)
f_parser.add_argument('item_description', help = 'include the item description.', required = True)
f_parser.add_argument('price', help = 'include the price.', required = True)
f_parser.add_argument('nutrition', help = 'include the nutritional content.', required = True)
