# Introduction

Dans le cadre du cours PYSEC (Python pour la sécurité) de l'EPITA, j'ai choisi
de développer un logiciel d'enregistrement de frappe, aussi connu sous le nom
de *keylogger*, ciblant les systèmes Linux.

## Pourquoi avoir choisi de faire un keylogger ?

Les keyloggers restent aujourd'hui une menace très importante pour les systèmes
d'information, il est donc intéressant de comprendre comment ils opèrent et
rien de mieux pour cela que d'en écrire un soi-même !

Le but de ce projet étant d'apprendre des choses sur la gestion des
périphériques d'entrée sous Linux, sur le fonctionnement d'un keylogger et sur
l'utilisation de Python dans le monde de la cybersécurité, j'ai choisi de
n'utiliser aucune bibliothèque externe au langage.

# Gestion des périphériques d'entrée sous Linux

La première chose à faire lorsque l'on souhaite développer un keylogger est de
se renseigner sur la manière dont l'OS ciblé gère les périphériques d'entrée
(dont font partie les claviers).

## "Everything is a file"

Sur Linux "tout est un fichier", les événements des périphériques d'entrée
peuvent être récupérés en lisant les fichiers[^1] associés dans `/dev/input`.
Par exemple, les événements de la souris peuvent être récupérés en lisant
`/dev/input/mice` (ce fichier combine tous les événements des souris dans le
cas où plusieurs sont connectées).  Cependant, il n'existe pas d'équivalent à
ce fichier pour les événements de clavier, il faut donc préalablement trouver
le fichier d'événement (`/dev/input/eventX`) associé.

[^1]: En réalité il ne s'agit pas de fichiers mais de *char devices*. Ce sont
  des interfaces vers des fonctions du noyau.

Pour cela, j'ai choisi de lire et parser le fichier `/proc/bus/input/devices`.
On aurait aussi pu utiliser les [ioctl](https://en.wikipedia.org/wiki/Ioctl) de
chaque fichier event pour déterminer les types d'événements qu'ils supportent.
En fonction des événements supportés, on est capable de distinguer un bouton
d'alimentation, un clavier, une souris, etc.

## Les événements

Il existe plusieurs types d'événements d'entrée que l'on peut retrouver
[ici](https://www.kernel.org/doc/html/latest/input/event-codes.html#event-types),
tous ne nous intéressent. Pour déterminer de quel type de périphérique il
s'agit, on peut se baser sur les événements qu'il supporte. Par exemple, dès
lors qu'un périphérique supporte les événements `EV_SYN`, `EV_KEY`, `EV_MSC`,
`EV_LED`, `EV_REP`, on peut considérer qu'il s'agit d'un clavier.

Une fois le périphérique détecté et identifié, il ne reste plus qu'à le "lire".
Les fichiers d'événements de périphériques se comportent d'une manière très
simple, ils écrivent au fur et a mesure qu'ils reçoivent les événements et ne
s'arrêtent jamais, cela les rend très pratique à lire en continu.

### Interprétation

Dans le kernel, les événements d'entrée sont représentés par la structure
suivante :
```c
struct input_event {
    struct timeval time;
    unsigned short type;
    unsigned short code;
    unsigned int value;
};
```

La récupération des événements se fait donc en lisant 24 octets par 24 octets
dans le fichier `eventX` associé au périphérique. Il faut ensuite reconstruire
la structure `input_event` pour pouvoir interpréter chacune des valeurs.

Dans le cas du keylogger, les événements qui nous intéressent sont
principalement ceux de type `EV_KEY`, déclenchés par les frappes sur les
touches.

### Les événements de frappes

Dans le cas d'une frappe, l'objet `input_event` émis est le suivant :
```c
struct input_event {
    struct timeval time; // Timestamp de l'événement (précis à la milliseconde)
    unsigned short type; // EV_KEY (0x01)
    unsigned short code; // Indique la touche concernée
    unsigned int value; // Indique si la touche a été : pressée, relâchée ou répétée
};
```

### Récupérer la touche

La dernière étape de "transformation" de l'événement pour le rendre "lisible"
est d'interpréter la touche et sa valeur (pressée, relâchée, répétée). Pour
cela, on peut récupérer les *keycodes* (codes de touches) dans le fichier
`/usr/include/uapi/linux/input-event-codes.h`[^2]

[^2]: Vous le retrouverez aussi dans les headers kernels
  (`/usr/lib/modules/<kernel>/build/include/uapi/linux/input-event-codes.h`),
  aussi disponibles
  [ici](https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h#L75)

# Place au code

Je ne détaillerai pas spécialement le code. Je trouve cependant intéressant
d'expliquer les choix que j'ai pû faire en développant.

Dès le début j'ai essayé de rendre mon code le plus "modulable" possible, de
manière à rendre l'implémentation de nouvelles fonctionnalités relativement
simple. Par exemple, vous pourrez observer une classe correspondant au "type"
de périphérique, ce qui rend plus facile le support d'autres périphériques
(comme les souris). Même si je n'ai pour l'instant pas prévu de continuer ce
projet à l'avenir, il me semblait tout de même important de designer le code de
cette manière.

Mon keylogger communique avec un serveur distant (qui réceptionne les frappes
enregistrées). Cette communication se fait à travers le protocole HTTP.
J'ai choisi ce protocole car il y a de grandes chances pour que ce dernier ne
soit pas bloqué par les pare-feu ou que ce soit détecté par les IDS/IPS[^3].
Évidemment, pour un "vrai" keylogger, il semble intéressant d'intégrer une
dimension cryptographique et/ou stéganographique à cette démarche de
dissimulation du malware.

[^3]: **I**ntrusion **D**etection **S**ystem / **I**ntrusion **P**revention
  **S**ystem, il s'agit de systèmes ayant pour but de détecter (et dans le cas
  des IPS, de bloquer) un traffic anormal sur le réseau.

Comme je l'ai mentionné en introduction, j'ai choisi de n'utiliser aucune
bibliothèque extérieur au langage. Pour moi, ce projet était l'occasion d'en
apprendre plus sur le langage et les modules de bibliothèque standard (au
passage, très complète).
Il est certain qu'en utilisant certaines bibliothèques (notamment pour
interpréter les frappes), j'aurais gagné du temps et écrit moins de ligne mais
ça n'était pas mon objectif.

Enfin, j'ai souhaité laisser une place à la flexibilité. C'est pourquoi
l'utilisateur, pourvu qu'il connaisse un peu Python, a la possibilité
d'implémenter ses propres "consommateurs" d'événements, de manière à filter les
événements, les afficher de manière différente, etc.

## Fonctionnalités et limitations connues
### Fonctionnalités

* Capture des frappes clavier
  Les frappes sont enregistrées et interprétées (le "nom" de la touche est
  affichée, exemple: `KEY_ESC` pour la touche Échap)
* Envoi de la capture à un serveur distant (chaque touche est envoyée en HTTP)
* Réception des touches envoyées (le keylogger fait à la fois client et serveur)
* Interprétation des touches par le client **ou** le serveur.
  De manière à réduire (sensiblement) le travail du client et la bande passante
  utilisée, on peut choisir d'envoyer les données *brutes* au serveur.
* Possibilité d'enregistrer les touches réceptionnées par le serveur

### Limitations connues
* Les périphériques de pointage (souris, trackpad, trackpoint, etc.) ne sont
  pas supportées
* Si la connexion avec le serveur est interrompue, les frappes ne sont plus
  enregistrées le temps que la connexion soit à nouveau établie
* Aucune option de sauvegarde locale
* Le keylogger ne tient pas compte de la disposition du clavier, ainsi en
  disposition *AZERTY*, un appui sur la touche A sera rapporté comme `KEY_Q`.
  ***Cela est dû au fait que la disposition du clavier n'est pas gérée par le
  kernel mais par le serveur d'affichage (e.g. Xorg)***

# Conclusion

Ce projet est loin d'être complet ou parfait mais il répond à l'exercice qui
était d'appliquer le langage Python au monde de la cybersécurité. Cela m'aura
permis d'en apprendre plus sur la gestion des événements d'entrée par le kernel
Linux, sur le fonctionnement d'un keylogger et c'était également un très bon
moyen de m'améliorer en Python.
