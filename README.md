# ScrapeStanovi #

Scrape stanova Beograd
Scrape skripta koja skida sa mojkvadrat.rs i sa halooglasi.com.
Ako vas ne zanima source code, ima tu i .bacpac za direktan import u SQL Azure.

## Prerequisites ##

* Instalirati [pyodbc](https://code.google.com/p/pyodbc/)
* Instalirati [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)
* Pre pokretanja treba imati neku bazu (SQL Server ili Azure)
* Na njoj izvrsiti initial.sql. On kreira tabele i sifarnike.
* Promeniti parametre baze u common.py

## Pokretanje ##

Bilo koji fajl moze da se pokrene. Skripta je jako mala tako da nema potrebe za objasnjavanjem icega.
Ono sto sam primetio je da halooglasi.com ne daju uvek neke boolean vrednosti (konkretno, lift), tako da
uzmite ove podatke sa rezervom.

## TODO ##

* Normalizacija i spajanje razlicitih source-ova (verovatno nikad)
* Bolji interfejs za promenu cene stana i nove stanove
