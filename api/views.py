from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from random import random

import json

#from .ai import minimax, alphabeta, alphabetaa
from .ai import minimax,alphabeta, allfabetaa

DEPTH_EASY = 3
DEPTH_MEDIUM = 3
DEPTH_HARD = 4

@csrf_exempt
def make_move(request):
    state = json.loads(request.body)
    difficulty = state['difficulty'] # tezinu igre 
    player = state['player'] # igrac koji je na potezu
    line_made = state['line_made'] # linija koja je napravljena

    if difficulty == 'easy': # ako je tezina igre laka
        _, move = minimax(state, DEPTH_EASY, player, line_made) 
    elif difficulty == 'medium':
        _, move = alphabeta(state, DEPTH_MEDIUM, -100000, 100000, player, line_made)
    elif difficulty == 'hard':
        _, move = allfabetaa(state, DEPTH_HARD, player, line_made)
    
    return JsonResponse({ 'move': move })











