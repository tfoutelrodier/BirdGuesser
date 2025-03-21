# BirdGuesser

## Game principle
An educational game about learning bird songs. 

Listen to songs and try to recognize which bird it is.
You can also train by listening to specific birds.

This is still a work in progress.

## Installation

The webapp is hosted at https://bird-guesser.vercel.app/
WARNING not fully functionning at the moment. Working on it

To run locally
```
git clone https://github.com/tfoutelrodier/BirdGuesser
# activate venv or equivalent of choice here if want to use one.
pip install -r BirdGuesser/requirements.txt
flask --run BirdGuesser/flaskr
```

## Origin

Several familly members were learning bird songs and I though it would be a nice project to try and make something for them.
I also wanted to learn how to make simple webapps. I knew python and the bases of HTML and CSS so I decided to try my hand at Flask for this project. 

Similar games exists and can be found on the internert but this one I can customize how I want.

## Data

Bird sound data was obtained from xenecanto database (https://xeno-canto.org/)
ALl French birds were recovered from this database (script data/french_bird_data_extraction.py)
Bird sound are loaded from xenocanto using their API.


