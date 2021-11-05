# Introduction

Dans le cadre du cours PYSEC (Python pour la sécurité), j'ai choisi de
développer un logiciel d'enregistrement de frappe, aussi connu sous le nom de
*keylogger*, ciblant les systèmes Linux.

## Pourquoi avoir choisi de faire un keylogger ?

Les keyloggers restent aujourd'hui une menace très importante pour les systèmes
d'information, il est donc intéressant de comprendre comment ils opèrent et rien
de mieux pour cela que d'en écrire un soi-même !

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
peuvent être récupérés en lisant les fichiers[^1] associés dans `/dev/input`. Par
exemples, les événements de la souris peuvent être récupérés en lisant
`/dev/input/mice` (ce fichier combine tous les événements des souris dans le cas
où plusieurs sont connectées).  Cependant, il n'existe pas d'équivalent à ce
fichier pour les événements de clavier, il faut donc préalablement trouver le
fichier d'événement (`/dev/input/eventX`) associé.

[^1]: En réalité il ne s'agit pas de fichiers mais de *char devices*. Ce sont des interfaces vers des fonctions du noyau.

Pour cela, j'ai choisi de lire et parser le fichier `/proc/bus/input/devices`.
On aurait aussi pu utiliser les [ioctl](https://en.wikipedia.org/wiki/Ioctl) de
chaque fichier event pour déterminer les types d'événements qu'ils supportent.
En fonction des événements supportés, on est capable de distinguer un bouton
d'alimentation, un clavier, une souris, etc.

## Les événements

Il existe plusieurs types d'événements d'entrée que l'on peut retrouver
[ici](https://www.kernel.org/doc/html/latest/input/event-codes.html#event-types), tous ne nous intéressent pas. Ici, pour détecter que nous avons affaire à un
clavier, nous nous basons sur les événements `EV_KEY` et `EV_REP`. Dès lors
qu'un périphérique supporte ces événements, on peut considérer qu'il s'agit d'un
clavier.

Une fois le périphérique détecté et identifié, il ne reste plus qu'à le "lire".
Les fichiers d'événements de périphériques se comportent d'une manière très
simple, ils écrivent au fur et a mesure qu'ils reçoivent les événements et ne
s'arrêtent jamais, cela les rend très pratique à lire en continu.
