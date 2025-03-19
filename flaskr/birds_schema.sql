DROP TABLE IF EXISTS birds;

CREATE TABLE birds (
  uid INTEGER PRIMARY KEY AUTOINCREMENT,  /*uid for the database*/
  id INTEGER UNIQUE, /*xenocanto id*/
  gen TEXT DEFAULT NULL, /*genus*/
  sp TEXT DEFAULT NULL, /*species*/
  ssp TEXT DEFAULT NULL, /*subspecies*/
  en TEXT NOT NULL, /*english name*/
  cnt TEXT NOT NULL, /*Country of recording ?*/
  loc FLOAT NOT NULL, /*Full text of location*/
  lat FLOAT NOT NULL, /*lat and lon coordiantes*/ 
  lng TEXT NOT NULL,
  alt TEXT DEFAULT NULL, /* recording altitude*/
  type TEXT DEFAULT NULL, /* Song type (mating song...)*/
  sex TEXT DEFAULT NULL, /*bird sex*/
  stage TEXT DEFAULT NULL, /*adult, juvenile...*/
  method TEXT DEFAULT NULL, /*field recording or other*/
  url TEXT NOT NULL,  /*bird page url on xeno canto*/
  file TEXT NOT NULL,  /*download the bird sound using this url*/
  file_name TEXT NOT NULL,  /*downloaded file name*/
  sono TEXT DEFAULT NULL, /* String which is a dict with links to pngs of different sizes representing the song spectrogram. Keys are small, medium, large...*/
  lic TEXT DEFAULT NULL, /*copyright license*/
  q TEXT NOT NULL, /*recording quality, letter coded (A is best)*/
  length TEXT NOT NULL, /*recording length stored as a string 1:10 for ex*/
  time TEXT DEFAULT NULL, /*time of recording during the day*/
  date TEXT DEFAULT NULL,
  also TEXT DEFAULT NULL /*text which is a python list format including other birds latin name that can be heard in recording*/
);
