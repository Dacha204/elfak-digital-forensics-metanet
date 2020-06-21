# Forenzika mrežnog saobracaja - praćenje putem metapodataka

[TOC]

---





----

# Skica

## Uvod

- Sta je forenzika, cime se bavi
- Koji su ciljevi forenzike
- Koje su sve grane forenzike
- Forenzika mreznog saobracaja, sta je, koji su ciljevi
- Tipovi mrezne forenzike:
  - can-you-catch
  - "offline" forenzika
- Po cemu se mrezna forenzika razlikuje od od ostalih grana forenzike,

- Metode u forenzici



Pracanje

- Metode pracenja

- Metadata pracenje

  - Sta su metadata podaci
  - Kako moze "anonimizovani" korisnik da se prati i prati njegove navike-

- Mrezni podaci:

  - Struktura podataka, kako funkcionse, koji su delovi
    - Protokoli, vrste paketa
  - Sta je korisno da se tretira kao metapodatak
    - IP adresa: Koji racunar i destinacija
    - Port: o kojoj aplikaciji je rec
    - Detekcija protokola

- Web pracenje:

  - HTTP protokol
  - HTTPS protokol, zasto se ne moze pratiti sadrzaj
  - Ali moze na nizem nivou da se prati na osnovu TCP/IP protokola

## Metanet projekat

- Njegova  uloga: na osnovu snimljenih podataka iz .pcap formata (Wireshark), ekstrktovanje korisnik paketa i vizualizacija peterna komunikacija korisnika.
-  Cilj je da se na osnovu paketa zakljuci aktivnost korisnika, koje web servise najvise koristi, u komp periodu se oni koriste u odredjenom vremenskom periodu.
- Mogucnost filtriranja rezultata

### Princip rada



__diagram__

PC ==> Server1 

​      ==> Server2

__pipeline_diagram__



Detekcija svih servera. Sa servera je dostupan samo samo IP adresa i port. Zelimo da na osnovu IP adresa saznamo o kom servisu se radi. Procesom analize se dolazi do identifikacije hosta. Zatim se podaci grupisu i  pravi vizualizacija podataka. Na osnovu vizualizacije se zapazaju trendovi u komunikaciji. Zapazacu u komunikaciji se szatim zapazaju trendovi 

- DNS Protokol, sta je i kako radi
- Problem u reverse DNS
  - Objasniti shared IP koncept u webserverima i virtualnog hosta (Host header)
- Resenje reverse dns-a i DHCP protkola (Wireshark builtin mehanizam)



Sada kad imamo naziv severa, filtriranje servera i povezivanje sa odgovarajucem servisom

#### Filtriranje rezultata

- Filtriranje reklama
  - Kako je obavljeno:
    - koriscenjem online kataloga
      - lista kojih kataloga je iskorisceno
- Filtriranje CDN servisa
  - Sta je CDN i cemu sluzi
  - Cemu smeta u analizi
  - Kako se filtriranje obavljeno

#### Vizualizacija

Korisceni software, Kibana & elasticsearch. Njihove mogucnosti:

- Indeksiranje i pretrazivanje ogromnog broja podataka
- Kibana: vizualizacija pretraga

#### Ubacivanje u elasticsearch & indeksiranje

- sta je iskorsceno od pcap podataka, i kako izgleda indeks
- ubacivanje podataka

#### Pretrazivanje i vizualziacija u kibani

- Vrste vizualizacija, tipovi, (Chartbar, plotter, etc)
- Heatmap objasnjen, njegove pogodnosti
- Primena heatmapa na nase podatke
- Limitiranje vremenskog perioda i kako se radi



## Literatura etc..

