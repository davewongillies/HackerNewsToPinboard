# Hacker News to Pinboard

Synchronize saved stories on Hacker News with Pinboard.in.

The script parses the saved stories page on [HN](http://news.ycombinator.com) and, for each link on the first page, it saves the story's link to [Pinboard](http://pinboard.in), using the [REST Pinboard API](https://pinboard.in/api).

The script is meant to be launched periodically by a scheduler (cron, etc.)

Originally developed on iPad with the awesome [Pythonista](http://omz-software.com/pythonista/)

## How to use ##

```
python hn2pin.py [hn user] [hn password] [pinboard.in token]
```

The Pinboard.in token is available [here](http://pinboard.in/settings/password)

## TODO ##

- Parse also the second page of HN saved stories
- Better handling of the script's input parameters
