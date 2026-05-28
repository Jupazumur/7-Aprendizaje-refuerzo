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

        self.estados = [(suma_jugador, carta_crupier, as_usable) 
                         for suma_jugador in range(12, 22) 
                         for carta_crupier in range(1, 11) 
                         for as_usable in [True, False]]

        self.estado_terminal = -1
        self.estados.append(self.estado_terminal)

        self.acciones = [0, 1] # Plantarse, Pedir
        
    def estado_inicial(self):
        
        self.cartas_jugador = [self.reparte_carta(), self.reparte_carta()]
        self.cartas_crupier = [self.reparte_carta(), self.reparte_carta()]

        suma_jugador, as_usable = self._evaluar_mano(self.cartas_jugador)

        self.blackjack_natural = self._checar_blackjack_natural(suma_jugador)

        while suma_jugador < 12:
            self.cartas_jugador.append(self.reparte_carta())
            suma_jugador, as_usable = self._evaluar_mano(self.cartas_jugador)

        return (suma_jugador, self.cartas_crupier[1], as_usable)

    def acciones_legales(self, s):

        return [] if s == self.estado_terminal else self.acciones
    
    def recompensa(self, s, a, s_):
        
        if s_ == self.estado_terminal and s != self.estado_terminal:
            
            suma_j = self._evaluar_mano(self.cartas_jugador)[0]
            suma_c = self._evaluar_mano(self.cartas_crupier)[0]

            if self.blackjack_natural and a == 0:
                return 1.5
            if suma_j > 21:
                return -1
            if suma_c > 21:
                return 1
            if suma_j > suma_c:
                return 1
            if suma_j == suma_c:
                return 0
            return -1
        
        return 0.0
    
    def transicion(self, s, a):

        if s == self.estado_terminal:
            return self.estado_terminal

        if a == 1: # Pedir
            self.cartas_jugador.append(self.reparte_carta())
            suma_jugador, as_usable = self._evaluar_mano(self.cartas_jugador)

            if suma_jugador > 21:
                return self.estado_terminal
            else:
                return (suma_jugador, self.cartas_crupier[1], as_usable)

        elif a == 0: # Plantarse
            suma_crupier = self._evaluar_mano(self.cartas_crupier)[0]
            
            while suma_crupier < 17:
                self.cartas_crupier.append(self.reparte_carta())
                suma_crupier = self._evaluar_mano(self.cartas_crupier)[0]
            
            return self.estado_terminal
    
    def es_terminal(self, s):
        return True if s == self.estado_terminal else False
    
    @staticmethod
    def reparte_carta():
        from random import choice
        return choice(BARAJA)
    
    def _evaluar_mano(self, cartas):
        """
        Regresa tupla (suma, as_usable)
        """
        suma = sum(cartas)
        if 1 in cartas and suma + 10 <= 21:
            return suma + 10, True
        else:
            return suma, False
    
    def _checar_blackjack_natural(self, suma_cartas):
        return True if suma_cartas == 21 else False


if __name__ == "__main__":

    blackjack = BlackJack(gama=1)

    Q_sarsa = SARSA( blackjack, alfa=0.05, epsilon=0.1, n_ep=500000, n_iter=25)
    Q_learning = Q_learning( blackjack, alfa=0.05, epsilon=0.1, n_ep=500000, n_iter=25)

    # # Encuentra las políticas óptimas para cada algoritmo
    pi_s = PoliticaGreedy(Q_sarsa)
    pi_q = PoliticaGreedy(Q_learning)

    # Imprime las políticas óptimas para cada estado no terminal
    print("Estado".center(20) + '|' +  "SARSA".center(20) + '|' + "Q-learning".center(20))
    print("-"*20 + '|' + "-"*20 + '|' + "-"*20)
    for s in blackjack.estados:
        if not blackjack.es_terminal(s):
            print(str(s).center(20) + '|' 
                  + str(pi_s(s)).center(20) + '|' 
                  + str(pi_q(s)).center(20))
    print("-"*20 + '|' + "-"*20 + '|' + "-"*20)


"""
****************************************************************************************
Responde las siguientes preguntas:

1. ¿Cuáles son los estados, acciones, recompensas y transiciones en el problema del 
    blackjack?

    - Los estados se representan con una tupla con la suma de la mano del jugador, la
      carta visible del crupier y un booleano que representa si tiene o no un as usable
      (cuando tomarlo como 11 no se pase de 21). Los estados son todas las permutaciones
      que son 200.

    - Las acciones son 0 - plantarse, 1 - pedir.

    - Las recompensas son +1.5 por blackjack natural, +1 por ganar, 0 por empate y -1
      por perder (ya sea por pasarse de 21 o por que el crupier tiene mejor mano).

    - Las transiciones describen la logica del juego dado un estado s y una acción a:
      si el jugador pide, evaluamos su nueva mano y checamos que no se pase. Si se plan-
      ta el juego se acaba y nos vamos a la función de recompensa.

2. ¿Cómo se pueden representar los estados del blackjack de manera eficiente para el 
    aprendizaje por refuerzo?

    A partir de un valor de 12 en suma de mano es cuando las decisiones se vuelven
    críticas. Sería de poca utilidad modelar desde el 1/A hasta el 11: la mejor
    acción siempre es pedir ya que el valor más grande que podemos jalar es 10,
    que resulta en 21 (en 11). A partir del 12 se pasa. Entonces se recorta el rango
    a [12, 21] y pasamos de 2100 estados a 200 estados.

3. ¿Qué pasa si se modifica el valor de epsilón de la política epsilon-greedy?

    Epsilon simboliza la relación explorar-explotar, entonces si fuera 0.5 por ejemplo,
    haría la mejor acción que conoce la mitad de las veces y una aleatoria la otra mitad.
    Entonces al subir o bajarla modificas que tan seguido usa su conocimiento adquirido
    y que tan seguido hace una acción aleatoria.

4. ¿Cómo afecta el valor de alfa en la convergencia de los algoritmos SARSA y Q-learning?

    El valor de alfa, la tasa de aprendizaje, controla que tan rápido aprenden los algo-
    ritmos. Si es muy alto, no llegan a una política estable porque los valores fluctúan
    demasiado (no convergen). Si es muy bajo si llegan a converger con una política estable
    e incluso óptima, pero lo harán demasiado lento.

5. ¿Cuál de los dos algoritmos, SARSA o Q-learning, consideras que es más adecuado para 
   el problema del blackjack y por qué?

   Para el problema del blackjack, Q-Learning: El SARSA, al usar acciones que toma el agente
   para actualizar sus valores, puede contaminar la política al penalizar sus errores.
   Suele crear una política conservadora y subóptima. El Q-Learning, al ser off-policy, toma
   en cuenta solo las mejores acciones para cada estado independientemente de las acciones
   que tome el agente y por ende está garantizado (dado el tiempo suficiente) a encontrar
   la mejor política.

   Para este proyecto en particular, el SARSA dominó en general porque usamos parámetros
   fijos y porque usamos episodios. Ambas limitan la utilidad del Q-Learning.

6. ¿Se puede explicar con cierta lógica del juego la política óptima encontrada por cada 
   algoritmo? ¿Qué acciones se toman en cada estado y por qué?

   https://www.blackjackapprenticeship.com/blackjack-strategy-charts/
   
   Si, como se puede ver en resultados.txt, dado los parámetros y episodios suficientes
   se puede llegar a una política casi igual a la óptima descrita en el enlace con ambos
   algoritmos.

   En mas_resultados.txt se encuentran más pruebas y descripciones del comportamiento.

****************************************************************************************
"""
