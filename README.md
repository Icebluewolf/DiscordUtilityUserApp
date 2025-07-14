## Discord Dev Utility User App
This is a user app that contains a variety of features that I personally think are useful.
It is intended to be my personal user app and all the features will cater to my needs.

Made with Python and Py-cord.
Uses Components V2 to offer a nice looking visual experience.
Sqlite is the database of choice for this project. It is in the `bot/database` directory.

Currently, The Features Are:
- Color Utilities: Show an image of a color based on the given hex or RGB.
  - I decided to manually create the PNG binary for this.
- Converters: Change bases, decoding to/from string, etc.
- Discord Utilities: Info About a snowflake (ID) and converting a datetime into a discord formatted date.
- Discord Help Center: Allows me to link discord help center articles by searching for the title.
Also posts notifications on a periodic basis for new and updated articles.
- User Tags: Much like a guild based tag system but tags are saved per user. Aliases are also supported.
Useful for saving links that you need to post frequently.
- Triggers: The webhook based notification system. Allows other features to hook into it. 
Manages the webhook urls for each event.