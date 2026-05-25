"""
El problema del blackjack simplificado como un problema de aprendizaje por refuerzo

"""

from RL import MDPsim, SARSA, Q_learning, PoliticaGreedy
from random import random, randint
BARAJA = [1,2,3,4,5,6,7,8,9,10,10,10,10]

class BlackJack(MDPsim):
    """
    Clase que representa un MDP para el problema del jugador.
    
    El jugador tiene un capital inicial y el objetivo es llegar a un capital
    objetivo o quedarse sin dinero.
    
    """
    def __init__(self, gama):
        self.cartas_jugador = []
        self.cartas_crupier = []
        self.estados = []
        self.gama = gama

        for suma_jugador in range(12,22):
            for carta_crupier in range(1,11):
                for as_usable in [True, False]:
                    self.estados.append(suma_jugador, carta_crupier, as_usable)

        self.estado_terminal = "Terminal"
        self.estados.append(self.estado_terminal)

        self.acciones = ["Plantarse", "Pedir"]
        
    def estado_inicial(self):
        self.cartas_jugador = [self.reparte_carta(), self.reparte_carta()]
        self.cartas_crupier = [self.reparte_carta(), self.reparte_carta()]

        suma_jugador, as_usable = self.evaluar_mano(self.cartas_jugador)

        self.blackjack_natural = self._checar_blackjack_natural(suma_jugador)

        while suma_jugador < 12:
            self.cartas_jugador.append(self.reparte_carta())
            suma_jugador, as_usable = self._evaluar_mano(self.cartas_jugador)

        return (suma_jugador, self.cartas_crupier[1], as_usable)

    def acciones_legales(self, s):

        return [] if s == self.estado_terminal else self.acciones
    
    def recompensa(self, s, a, s_):
        # TODO: implementar la recompensa del blackjack
        raise NotImplementedError("Implementa la recompensa del blackjack")
    
    def transicion(self, s, a):

        if a == "Pedir":
            self.cartas_jugador.append(self.reparte_carta())
            suma_jugador, as_usable = self._evaluar_mano(self.cartas_jugador)

            if suma_jugador > 21:
                return self.estado_terminal
            else:
                return (suma_jugador, self.cartas_crupier[1], as_usable)

        elif a == "Plantarse":
            while sum(self.cartas_crupier) < 17:
                self.cartas_crupier.append(self.reparte_carta())
                suma_crupier = self._evaluar_mano(self.cartas_jugador)[0]
            
            return self.estado_terminal
    
    def es_terminal(self, s):
        return True if s == self.estado_terminal else False
    
    def reparte_carta():
        from random import choice
        return choice(BARAJA)
    
    def _evaluar_mano(self, cartas):
        """
        Regresa tupla (suma, as_usable)
        """
        suma = sum(cartas)
        return suma + 10, True if (1 in cartas and suma <= 21) else suma, False
    
    def _checar_blackjack_natural(self, suma_cartas):
        return True if suma_cartas == 21 else False


if __name__ == "__main__":
    pass

    # blackjack = BlackJack(gama=1,...) # TODO: agregar los parámetros necesarios para el blackjack   

    # # TODO: definir los parámetros de SARSA y Q-learning, luego crear las instancias 
    # # de cada algoritmo
    # Q_sarsa = SARSA( blackjack, alfa=..., epsilon=..., n_ep=..., n_iter=...)
    # Q_learning = Q_learning( blackjack, alfa=..., epsilon=..., n_ep=..., n_iter=...)

    # # Encuentra las políticas óptimas para cada algoritmo
    # pi_s = PoliticaGreedy(Q_sarsa)
    # pi_q = PoliticaGreedy(Q_learning)

    # # Imprime las políticas óptimas para cada estado no terminal
    # print("Estado".center(10) + '|' +  "SARSA".center(10) + '|' + "Q-learning".center(10))
    # print("-"*10 + '|' + "-"*10 + '|' + "-"*10)
    # for s in blackjack.estados:
    #     if not blackjack.es_terminal(s):
    #         print(str(s).center(10) + '|' 
    #               + str(pi_s(s)).center(10) + '|' 
    #               + str(pi_q(s)).center(10))
    # print("-"*10 + '|' + "-"*10 + '|' + "-"*10)


"""
****************************************************************************************
Responde las siguientes preguntas:

1. ¿Cuáles son los estados, acciones, recompensas y transiciones en el problema del 
    blackjack?  

2. ¿Cómo se pueden representar los estados del blackjack de manera eficiente para el 
    aprendizaje por refuerzo?

3. ¿Qué pasa si se modifica el valor de epsilón de la política epsilon-greedy?

4. ¿Cómo afecta el valor de alfa en la convergencia de los algoritmos SARSA y Q-learning?

5. ¿Cuál de los dos algoritmos, SARSA o Q-learning, consideras que es más adecuado para 
   el problema del blackjack y por qué?

6. ¿Se puede explicar con cierta lógica del juego la política óptima encontrada por cada 
   algoritmo? ¿Qué acciones se toman en cada estado y por qué?
****************************************************************************************
"""
