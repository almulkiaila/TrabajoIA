from collections import deque
import heapq
import time
import numpy as np
import random


class WaterSortGame:
    def __init__(self, num_tubes,num_colors,seed):
            self.num_tubes = num_tubes
            self.num_colors = num_colors
            self.capacity = 4
            self.seed = seed
            self.initial_state = self.generate_initial_state()
    def generate_initial_state(self):
        if self.seed is not None:
            random.seed(self.seed)
            np.random.seed(self.seed)

        # Create a list whith colors in order    
        colors = np.repeat(np.arange(1, self.num_colors + 1), self.capacity)
        

        # Shuffle the list
        np.random.shuffle(colors)
        # Add the empty tubes and create the matrix
        total_slots = self.num_tubes * self.capacity
        if len(colors) < total_slots:
            zeros = np.zeros(total_slots - len(colors), dtype=int)
            colors = np.concatenate((colors, zeros))
        state = colors.reshape((self.num_tubes, self.capacity))
        return state
    

    def is_goal_state(self,state):
        is_valid = True
        i=0
        while i<self.num_tubes and is_valid:
            color = state[i,0]
            j=1
            while j<self.capacity and is_valid:
                if(state[i,j]!=color):
                    is_valid = False
                j+=1
            i+=1
        return is_valid



    def is_valid_state(self,t_origen, t_destino):
        is_valid = -1
        o_empty = self.is_empty(t_origen)
        if o_empty: 
            return -1
       
        d_empty = self.is_empty(t_destino)
        if d_empty:
            is_valid = self.capacity
        else:
             org_contents = self._contents_left(t_origen)
             dst_contents = self._contents_left(t_destino)
             lorigen = self._top_block_len(org_contents)
             cap_tube_dst = self.capacityTube(t_destino)

             if org_contents[0]==dst_contents[0] and lorigen <= cap_tube_dst:
                 is_valid = cap_tube_dst

        return is_valid

                 
    def position_first_color(self,tube):
        j = 0
        not_found = True
        while j<self.capacity and not_found:
            if(tube[j]!=0):
                not_found = False
            j+=1
        return j-1
    
    def capacityTube(self,tube):
        return np.sum(tube == 0)

    def is_empty(self,tube):
        is_empty = True
        i = 0
        while i<self.capacity and is_empty:
            if(tube[i]!=0):
                is_empty = False
            i+=1
        return is_empty

    def state_to_tuple(self, state):
        state = np.array(state, dtype=int)
        return tuple(tuple(int(x) for x in tube) for tube in state)

    
    def hash_state(self, state_tuple):
        sorted_tubes = tuple(sorted(state_tuple))
        return hash(sorted_tubes)

    
    def _contents_left(self, row):
        # todos los números q no sean 0 izq -> der
        return [int(x) for x in row if x != 0]


    #Este me calcula la longitud del ultimo color
    def _top_block_len(self, contents):
        if not contents:
            return 0
        c = contents[0]
        k = 1
        while k < len(contents) and contents[k] == c:
            k += 1
        return k
    
    
    # Convierte una lista de líquidos reales (sin ceros) en un tubo completo con ceros al final,
    #para representar los espacios vacíos.
    def _pack_row(self, contents):
        #arr = contents + [0] * (self.capacity - len(contents))
        arr = [0] * (self.capacity - len(contents)) + contents
        return np.array(arr, dtype=int)

    def get_valid_moves(self, state):
        moves = []
        #recorremos todos los tubos del estado, como origen
        for i in range(self.num_tubes):
            for j in range(self.num_tubes): #recorremos todos los tubos del estado, como destino
                if i == j:
                    continue #si son =, saltamos al siguiente j sin hacer nada.
                k = self.is_valid_state(state[i], state[j])
                if k != -1:
                    moves.append((i, j))
        return moves

    def apply_move(self, state, move):
        state = np.array(state, dtype=int)  
        i, j = move
        new_state = state.copy() # para no modificar el original

        src_row = new_state[i].copy() #origen 
        dst_row = new_state[j].copy() #destino
        #aqui nos quedamos con todos los colores , sin ceros
        src_contents = self._contents_left(src_row)
        dst_contents = self._contents_left(dst_row)



        color = src_contents[0] #el color q se va a verter
        block = self._top_block_len(src_contents)#num de unidades
        space = self.capacity - len(dst_contents)#cuantos huecos tiene el destino

        src_contents = src_contents[block:] #le quitamos el bloque de tam block
        dst_contents = [color] * block + dst_contents #añadimos al inicio del destino block copias de color.

        new_state[i] = self._pack_row(src_contents)
        new_state[j] = self._pack_row(dst_contents)
        return new_state

    


class SearchAlgorithm:
    def __init__(self, game):
        self.game = game

    def bfs(self, initial_state):
        t0 = time.time()
        ini_key = self.game.state_to_tuple(initial_state)
        ini_hash = self.game.hash_state(ini_key)

        if self.game.is_goal_state(initial_state):
            t1 = time.time()
            return [], {
                'nodos_expandidos': 0,
                'nodos_en_memoria_max': 1,
                'tiempo_seg': t1 - t0,
                'profundidad_solucion': 0
            }

        abiertos = deque([initial_state])  
        cerrados = set()
        abiertos_set = {ini_hash}    
        padre = {ini_key: None}               
        mov_que_lleva = {}                   

        nodos_expandidos = 0
        pico_memoria = len(cerrados) + len(abiertos)

        while abiertos:
            estado = abiertos.popleft()
            key_estado = self.game.state_to_tuple(estado)
            hash_estado = self.game.hash_state(key_estado)
            cerrados.add(hash_estado)
            nodos_expandidos += 1
            if self.game.is_goal_state(estado):
           
                camino = []
                cur = key_estado
                while padre[cur] is not None:
                    camino.append(mov_que_lleva[cur])
                    cur = padre[cur]
                camino.reverse()

                t1 = time.time()
                pico_memoria = max(pico_memoria, len(abiertos) + len(cerrados))
                stats = {
                    'nodos_expandidos': nodos_expandidos,
                    'nodos_en_memoria_max': pico_memoria,
                    'tiempo_seg': t1 - t0,
                    'profundidad_solucion': len(camino)
                }
                return camino, stats

            for movimiento in self.game.get_valid_moves(estado): # Expande el nodo
                nuevo_estado = self.game.apply_move(estado, movimiento)

                key = self.game.state_to_tuple(nuevo_estado)
                hash_new_state = self.game.hash_state(key)

                if hash_new_state not in cerrados and hash_new_state not in abiertos_set:
                    padre[key] = key_estado  
                    mov_que_lleva[key] = movimiento
                    abiertos.append(nuevo_estado)
                    abiertos_set.add(hash_new_state)
                    pico_memoria = max(pico_memoria, len(abiertos) + len(cerrados))

        t1 = time.time()
        stats = {
            'nodos_expandidos': nodos_expandidos,
            'nodos_en_memoria_max': pico_memoria,
            'tiempo_seg': t1 - t0,
            'profundidad_solucion': None
        }
        return cerrados, stats
    
    ######################################################################################################################
    def dfs(self, initial_state):
        t0 = time.time()
        ini_key = self.game.state_to_tuple(initial_state)
        ini_hash = self.game.hash_state(ini_key)

        if self.game.is_goal_state(initial_state):
            t1 = time.time()
            return [], {
                'nodos_expandidos': 0,
                'nodos_en_memoria_max': 1,
                'tiempo_seg': t1 - t0,
                'profundidad_solucion': 0
            }

        abiertos = deque([initial_state])  
        cerrados = set()
        abiertos_set = {ini_hash}    
        padre = {ini_key: None}               
        mov_que_lleva = {}                   

        nodos_expandidos = 0
        pico_memoria = len(cerrados) + len(abiertos)

        while abiertos:
            estado = abiertos.pop()
            key_estado = self.game.state_to_tuple(estado)
            hash_estado = self.game.hash_state(key_estado)
            cerrados.add(hash_estado)
            nodos_expandidos += 1
            if self.game.is_goal_state(estado):
           
                camino = []
                cur = key_estado
                while padre[cur] is not None:
                    camino.append(mov_que_lleva[cur])
                    cur = padre[cur]
                camino.reverse()

                t1 = time.time()
                pico_memoria = max(pico_memoria, len(abiertos) + len(cerrados))
                stats = {
                    'nodos_expandidos': nodos_expandidos,
                    'nodos_en_memoria_max': pico_memoria,
                    'tiempo_seg': t1 - t0,
                    'profundidad_solucion': len(camino)
                }
                return camino, stats

            for movimiento in self.game.get_valid_moves(estado): # Expande el nodo
                nuevo_estado = self.game.apply_move(estado, movimiento)

                key = self.game.state_to_tuple(nuevo_estado)
                hash_new_state = self.game.hash_state(key)

                if hash_new_state not in cerrados and hash_new_state not in abiertos_set:
                    padre[key] = key_estado  
                    mov_que_lleva[key] = movimiento
                    abiertos.append(nuevo_estado)
                    abiertos_set.add(hash_new_state)
                    pico_memoria = max(pico_memoria, len(abiertos) + len(cerrados))

        t1 = time.time()
        stats = {
            'nodos_expandidos': nodos_expandidos,
            'nodos_en_memoria_max': pico_memoria,
            'tiempo_seg': t1 - t0,
            'profundidad_solucion': None
        }
        return cerrados, stats
   
    
    ######################################################################################################################
    def a_star(self, initial_state, heuristic):
        t0 = time.time()
        ini_key = self.game.state_to_tuple(initial_state)
        ini_hash = self.game.hash_state(ini_key)

        if self.game.is_goal_state(initial_state):
            t1 = time.time()
            return [], {
                'nodos_expandidos': 0,
                'nodos_en_memoria_max': 1,
                'tiempo_seg': t1 - t0,
                'profundidad_solucion': 0
            }

        pendientes = []
        cont = 0  # desempate en heapq
        h0 = heuristic(initial_state)
        heapq.heappush(pendientes, (h0, 0, cont, initial_state))

        visitados = set()                # conjunto de hashes
        padre = {ini_key: None}          # claves = tuplas
        mov_que_lleva = {}
        g_cost = {ini_hash: 0}

        nodos_expandidos = 0
        pico_memoria = len(pendientes)

        while pendientes:
            f, g, _, estado = heapq.heappop(pendientes)
            key = self.game.state_to_tuple(estado)
            hash_key = self.game.hash_state(key)

            if hash_key in visitados:
                continue
            visitados.add(hash_key)
            nodos_expandidos += 1

            if self.game.is_goal_state(estado):
                camino = []
                cur = key
                while padre[cur] is not None:
                    camino.append(mov_que_lleva[cur])
                    cur = padre[cur]
                camino.reverse()

                t1 = time.time()
                pico_memoria = max(pico_memoria, len(pendientes) + len(visitados))
                stats = {
                    'nodos_expandidos': nodos_expandidos,
                    'nodos_en_memoria_max': pico_memoria,
                    'tiempo_seg': t1 - t0,
                    'profundidad_solucion': len(camino)
                }
                return camino, stats

            # Expandimos movimientos válidos
            for movimiento in self.game.get_valid_moves(estado):
                nuevo_estado = self.game.apply_move(estado, movimiento)
                key_new = self.game.state_to_tuple(nuevo_estado)
                hash_new = self.game.hash_state(key_new)

                g_new = g + 1
                f_new = g_new + heuristic(nuevo_estado)

                # Solo añadimos si no está visitado o si mejora el coste
                if hash_new not in visitados and (hash_new not in g_cost or g_new < g_cost[hash_new]):
                    padre[key_new] = key
                    mov_que_lleva[key_new] = movimiento
                    g_cost[hash_new] = g_new
                    cont += 1
                    heapq.heappush(pendientes, (f_new, g_new, cont, nuevo_estado))

            pico_memoria = max(pico_memoria, len(pendientes) + len(visitados))

        # Si no hay solución
        t1 = time.time()
        stats = {
            'nodos_expandidos': nodos_expandidos,
            'nodos_en_memoria_max': pico_memoria,
            'tiempo_seg': t1 - t0,
            'profundidad_solucion': None
        }
        return None, stats

######################################################################################################################
    def h1(self,state):
        colors = np.unique(state[state!=0])
        h = 0
        for color in colors:
            count = np.array([np.sum(tube == color) for tube in state])
            tubes_with_color = np.sum(count>0)

            if tubes_with_color <=1:
                continue
            
            main_tube_idx = np.argmax(count)
            main_amount = count[main_tube_idx]

            weight_dispersion = np.sum(count) - main_amount

            h+= (tubes_with_color-1)*weight_dispersion
        return h
    
    def h2(self,state):
        incomplete_tubes = 0
        well_positioned_colors = 0

        for tube in state:
            colors = [c for c in tube if c!=0]

            if len(colors) == 0:
                continue
            if len(colors)==4 and all(c==colors[0] for c in colors):
                continue

            incomplete_tubes+=1

            if len(colors)>0:
                lc = len(colors)
                base_color = colors[-1]
                consecutive = 1
                for i in range(lc-2,-1,-1):
                    if colors[i] == base_color:
                        consecutive+=1
                    else:
                        break
            well_positioned_colors+=consecutive
        h = (incomplete_tubes*4)-well_positioned_colors
        return h
    



    def h3(self, state):
   
        total_mezcladas = 0
        total_bloqueadas = 0

        for tube in state:
            #contenidos reales sin ceros
            contents = [int(c) for c in tube if c != 0]
            if not contents:
                continue

            
            #aqui contamos cuantos colores distintos hay en el tubo
            colores_distintos = len(set(contents))
            if colores_distintos > 1:
                #todas cuentn como mezcladas
                total_mezcladas += len(contents)

                # contamos cuants de arriba son de color distinto
                for i in range(len(contents)):
                    ci = contents[i] #color del bloque actual
                    # mira los de arriba: indices [0..i-1]
                    for j in range(i):
                        #si alguna de las de arriba es de distinto color, la unidad está bloqueada
                        if contents[j] != ci:
                            total_bloqueadas += 1
           

        return total_mezcladas + 2 * total_bloqueadas




'''''

def print_state(state):
    for i, row in enumerate(state):
        print(f"Tubo {i}: {row.tolist()}")

def apply_path_and_show(game, state, path):
    cur = state.copy()
    for (i, j) in path:
        cur = game.apply_move(cur, (i, j))
    return cur
'''''

