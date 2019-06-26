
# Greenify

A project to create fake commits that look (kinda) realistic! No legitimate reason to be using this, but who am I to judge?

## Dependencies

Need Python3, and some standard libraries like pandas, numpy and dateutils. And git of course.
This only works on linux and mac for now.

## Usage

For detailed instructions
```
python3 greenify.py --help
```

## How it works

It create a non-homogenous poisson random process between two dates.
Then fakes the author date and the commit date of the git commit.

## License
MIT