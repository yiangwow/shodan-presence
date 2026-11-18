"""Shuffled decks: a pool is dealt without repeats until it is spent."""

import random

_decks = {}  # pool name -> shuffled cards still to deal


def draw(name, pool):
    """Deal from a shuffled deck: no card repeats until the pool is spent."""
    deck = _decks.get(name)
    if not deck:
        deck = list(pool)
        random.shuffle(deck)
        _decks[name] = deck
    return deck.pop()
