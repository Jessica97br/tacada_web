#Para iniciar o jogo usar o cd /d D:\SSD\Python\tacada e depois : .venv\Scripts\python.exe main.py
#Verificar como colocar ele online*Claude diz que tem uma opção de usar o proprio pybag para colocar ele no navegador, podemos testar*ver no github também*
import pygame
import random # importa o movimento aleatório 
import math # a biblioteca de matemática do Python
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.mixer.pre_init(44100, -16, 2, 512) # (frequency, size, channels, buffer)
pygame.init()

LARGURA = 800
ALTURA = 500

tela = pygame.display.set_mode(
    (LARGURA, ALTURA)
)  # Cria o display do jogo conforme o tamanho de tela definido em altura e largura
pygame.display.set_caption(
    "TACADA!"
)  # Informa o titulo do jogo no display da tela do Pygame, é possível alterar para multifases, criando uma variável

clock = pygame.time.Clock()  # Controla a velocidade do jogo

# ============================================================
# FONTES DO JOGO
# ============================================================
fonte = pygame.font.Font(None, 36)
fonte_titulo = pygame.font.Font(None, 50)
fonte_pequena = pygame.font.Font(None, 28)

# Foi necessário colocar os atributos do campo, jogador e bola antes do while para que o jogo possa se manter em looping, sem essa alteração a bola não se movimenta

# ============================================================
# CARREGAMENTO DAS IMAGENS
# ============================================================
bola_img = pygame.image.load("imagens/bola.png").convert_alpha() #convert alpha deixa as imagens em fundo transparente
personagem_img = pygame.image.load("imagens/personagem.png").convert_alpha()
braco_img = pygame.image.load("imagens/braco.png").convert_alpha()
taco_img = pygame.image.load("imagens/taco.png").convert_alpha()
lancador_img = pygame.image.load("imagens/lancador.png").convert_alpha()
# Rotaciona o lançador 90 graus para a esquerda
lancador_img = pygame.transform.rotate(lancador_img, 90)
tela_inicial = pygame.image.load("imagens/tela_inicial.jpg").convert_alpha()
tela_game_over = pygame.image.load("imagens/tela_game_over.png").convert_alpha()
textura_gramado = pygame.image.load("imagens/gramado.jpeg").convert_alpha()
arquibancada = pygame.image.load("imagens/arquibancada.png").convert_alpha()

# ============================================================
# CARREGAMENTO DOS SONS
# ============================================================
som_bola_ar = pygame.mixer.Sound("sons/air_ball.wav")
som_taco = pygame.mixer.Sound("sons/bat_hit.wav")
som_organ = pygame.mixer.Sound("sons/organ_baseball.wav")
fundo = pygame.mixer.Sound("sons/fundo.wav")
som_game_over = pygame.mixer.Sound("sons/game_over.wav")
som_estadio = pygame.mixer.Sound("sons/som_estadio.wav")


som_bola_ar.set_volume(0.5)
som_taco.set_volume(0.8)
som_organ.set_volume(0.3)
som_game_over.set_volume(0.6)
som_estadio.set_volume(0.15)
fundo.set_volume(0.3)
fundo.play(-1)   # -1 = repete para sempre

# ============================================================
# AJUSTE DA IMAGEM DA ARQUIBANCADA
# ============================================================

arquibancada = pygame.transform.scale(
    arquibancada,
    (LARGURA, 300)
)

# ============================================================
# AREA DO CAMPO
# ============================================================

largura_campo = LARGURA
x_campo = 0

# Onde o gramado começa no centro do fundo (fim da linha branca)
y_campo = 210
altura_campo = ALTURA - y_campo   # o campo vai até o fim da tela

# ============================================================
# SUPERFÍCIE DO CAMPO
# ============================================================
campo_superficie = pygame.Surface(
    (largura_campo, altura_campo),
    pygame.SRCALPHA
)

textura_campo_redimensionada = pygame.transform.scale(
    textura_gramado,
    (largura_campo, altura_campo)
)
campo_superficie.blit(textura_campo_redimensionada, (0, 0))

# ============================================================
# MÁSCARA OVAL ACHATADA (elipse mais larga que a tela)
# ============================================================
mascara_campo = pygame.Surface(
    (largura_campo, altura_campo),
    pygame.SRCALPHA
)

# Quanto a elipse ultrapassa cada lado da tela.
# Maior = a curva daquele lado fica mais alta (cobre mais o fundo)
excesso_esquerdo = 115
excesso_direito = 170   # aumente para cobrir mais o lado direito

pygame.draw.ellipse(
    mascara_campo,
    (255, 255, 255, 255),
    (
        -excesso_esquerdo,                                      # começa fora da tela, à esquerda
        0,                                                      # topo encostado no chão do fundo
        largura_campo + excesso_esquerdo + excesso_direito,     # largura total da elipse
        altura_campo                                            # base na borda inferior
    )
)

campo_superficie.blit(
    mascara_campo,
    (0, 0),
    special_flags=pygame.BLEND_RGBA_MULT
)

# ============================================================
# AREA DO PITCH
# ============================================================
# O pitch ocupa uma boa parte do centro do campo
largura_pitch = 560
altura_pitch = 110

# Centraliza o pitch dentro do campo
x_pitch = x_campo + (largura_campo - largura_pitch) // 2
y_pitch = y_campo + (altura_campo - altura_pitch) // 2

# ============================================================
# JOGADOR EM RELACAO AO CAMPO
# ============================================================
# Agora: exatamente em cima da linha lateral direita do pitch
x_jogador = x_pitch + largura_pitch - int(largura_pitch * 0.15)
y_jogador = y_pitch + altura_pitch // 2
# ============================================================
# LANÇADOR EM RELAÇÃO AO CAMPO
# ============================================================

# O lançador fica na extremidade oposta do pitch
x_lancador = x_pitch + largura_pitch * 0.12
y_lancador = y_pitch + altura_pitch // 2

# Taco espelhado uma única vez: cabo à direita (na mão), ponta à esquerda
taco_pronto = pygame.transform.flip(taco_img, True, False)

# Braço espelhado uma única vez: a mão passa para a ponta esquerda (a que prende no taco)
braco_pronto = pygame.transform.flip(braco_img, True, False)

# ============================================================
# ALTURA DE REBATIDA DA BOLA EM RELACAO AO JOGADOR
# ============================================================
# A zona ocupa aproximadamente 30% do pitch
largura_zona = int(largura_pitch * 0.30)

# Começa antes do jogador
x_zona = x_jogador - largura_zona

# A zona acompanha o trecho entre as duas linhas de rebatida
y_crease_superior = y_pitch + int(altura_pitch * 0.12)
y_crease_inferior = y_pitch + int(altura_pitch * 0.88)

altura_zona = y_crease_inferior - y_crease_superior
y_zona = y_crease_superior


# ============================================================
# TEXTURA DESGASTADA DA ZONA DE REBATIDA (gerada uma única vez)
# ============================================================
superficie_desgaste = pygame.Surface((largura_zona, altura_zona), pygame.SRCALPHA)
superficie_desgaste.fill((150, 115, 70, 110))   # base de terra mais escura, semitransparente

# Manchas grandes, escuras e claras
for _ in range(25):
    cor = random.choice([
        (110, 80, 45, 80),     # terra escura
        (205, 175, 120, 70),   # terra clara / poeira
    ])
    mancha = pygame.Rect(
        random.randint(0, largura_zona),
        random.randint(0, altura_zona),
        random.randint(15, 40),
        random.randint(8, 18),
    )
    pygame.draw.ellipse(superficie_desgaste, cor, mancha)

# Pontinhos de sujeira
for _ in range(150):
    pygame.draw.circle(
        superficie_desgaste,
        (90, 65, 35, 120),
        (random.randint(0, largura_zona), random.randint(0, altura_zona)),
        random.randint(1, 2),
    )

# ============================================================
# BOLA EM RELACAO AO CAMPO
# ============================================================
x_inicial_bola = x_pitch + largura_pitch * 0.12
y_bola = y_pitch + altura_pitch // 2
x_bola = x_inicial_bola
velocidade_x = 3
velocidade_y = 0 # Define o movimento em y
bola_na_zona = False  # Indica que a bola ainda não chegou na zona de rebatida
game_over = False  # Indica que o jogo ainda não terminou
bola_rebatida = False  # Indica que a bola ainda não foi rebatida
bola_subindo = False
tempo_bola_parada = 0
# ============================================================
# EXPLICACAO MOVIMENTACAO DO OBJETO
# ============================================================    
# A depender do valor de x e y o movimento do objeto muda:
# velocidade_x > 0 → direita
# velocidade_x < 0 → esquerda
# velocidade_y > 0 → baixo
# velocidade_y < 0 → cima

# ============================================================
# ESTADO DO JOGO
# ============================================================
estado_jogo = "INICIO"  # Cria uma função de inicio do jogo que permite orientar o jogador antes de começar a jogar
tela_inicial = pygame.transform.scale(tela_inicial, (LARGURA, ALTURA))
tela_game_over = pygame.transform.scale(tela_game_over, (LARGURA, ALTURA))

# ============================================================
# FUNCAO PARA REINICIO DO JOGO
# ============================================================
def reiniciar_jogo():
    global velocidade_descida, tacando
    global x_bola, y_bola
    global velocidade_x, velocidade_y
    global bola_na_zona, game_over
    global bola_rebatida
    global estado_jogo
    global bola_subindo, tempo_bola_parada
    global pontuacao

    x_bola = x_inicial_bola
    y_bola = y_pitch + altura_pitch // 2

    velocidade_descida = 3
    velocidade_x = velocidade_descida
    tacando = False
    velocidade_y = 0

    bola_na_zona = False
    game_over = False
    bola_rebatida = False
    estado_jogo = "INICIO"
    bola_subindo = False
    tempo_bola_parada = 0
    pontuacao = 0
    
    som_estadio.stop()
    som_game_over.stop()
    fundo.stop()
    fundo.play(-1)
    

# ============================================================
# PONTUACAO DO JOGADOR
# ============================================================
rodando = True
pontuacao = 0  # Guarda a pontuação atual do jogador
tipo_tacada = ""
fase = 1
velocidade_descida = 3

# ============================================================
# VARIAVEIS DA ANIMACAO
# ============================================================
# Controla se o jogador está realizando uma tacada
tacando = False
# Guarda o momento em que a tacada começou
tempo_tacada = 0
# Duração total da animação da tacada
duracao_tacada = 150
# Ângulo atual da rotação do braço e do taco
angulo_tacada = 0
# Pequena rotação do personagem para aproximar o ombro direito da bola
angulo_personagem = 20

# ============================================================
# CONTORNO TEXTO TELA INICIAL
# ============================================================
def desenhar_texto_contorno(texto, fonte, cor_texto, cor_contorno, posicao):
    # Cria o texto principal
    texto_principal = fonte.render(texto, True, cor_texto)

    # Cria o contorno
    texto_contorno = fonte.render(texto, True, cor_contorno)
    x, y = posicao

    # Desenha o contorno em 4 direções
    tela.blit(texto_contorno, (x - 2, y))
    tela.blit(texto_contorno, (x + 2, y))
    tela.blit(texto_contorno, (x, y - 2))
    tela.blit(texto_contorno, (x, y + 2))

    # Desenha o texto principal por cima
    tela.blit(texto_principal, (x, y))
    
def blit_com_pivo(img, pivo_na_img, pos_pivo, angulo):
###Rotaciona a imagem em torno de um ponto (pivô) e desenha na tela.###
    centro = pygame.math.Vector2(img.get_rect().center)
    deslocamento = (pygame.math.Vector2(pivo_na_img) - centro).rotate(-angulo)
    rotacionada = pygame.transform.rotate(img, angulo)
    rect = rotacionada.get_rect(center=pos_pivo - deslocamento)
    tela.blit(rotacionada, rect)
            
# ============================================================
# CENÁRIO ESTÁTICO (desenhado uma única vez)
# ============================================================
cenario = pygame.Surface((LARGURA, ALTURA))
cenario.blit(arquibancada, (0, 0))
cenario.blit(campo_superficie, (x_campo, y_campo))
pygame.draw.rect(cenario, (190, 160, 100), (x_pitch, y_pitch, largura_pitch, altura_pitch))

# Linhas brancas
distancia_lateral = int(largura_pitch * 0.15)
x_esq = x_pitch + distancia_lateral
x_dir = x_pitch + largura_pitch - distancia_lateral
branco = (255, 255, 255)

for y in (y_crease_superior, y_crease_inferior):
    pygame.draw.line(cenario, branco, (x_pitch, y), (x_pitch + largura_pitch, y), 3)
for x in (x_esq, x_dir):
    pygame.draw.line(cenario, branco, (x, y_crease_superior), (x, y_crease_inferior), 3)

# Zona de rebatida
cenario.blit(superficie_desgaste, (x_zona, y_zona))
pygame.draw.rect(cenario, (200, 200, 120), (x_zona, y_zona, largura_zona, altura_zona), 2)

# Lançador
cenario.blit(lancador_img, (
    x_lancador - lancador_img.get_width() // 2,
    y_lancador - lancador_img.get_height()
))

personagem_pronto = pygame.transform.rotate(
    pygame.transform.flip(personagem_img, True, False), angulo_personagem
)

LIMITE_PERFEITA = 0.70
LIMITE_BOA = 0.35

TACADAS = {
    "PERFEITA": dict(pontos=100, velocidade=7, distancia=330, desvio=(0, 12)),
    "BOA":      dict(pontos=50,  velocidade=5, distancia=200, desvio=(10, 30)),
    "FRACA":    dict(pontos=10,  velocidade=4, distancia=90,  desvio=(25, 50)),
}

# Antes do loop: lê o recorde salvo (se o arquivo não existir, começa em 0)
try:
    with open("recorde.txt") as arquivo:
        recorde = int(arquivo.read())
except (FileNotFoundError, ValueError):
    recorde = 0
    
# ============================================================
# LOOP PRINCIPAL
# ============================================================

while rodando:
    for (
        evento
    ) in (
        pygame.event.get()
    ):  # Verifica cada evento realizado no jogo, por exemplo, se foi realizado um clique na tela ou apertada uma tecla

        if evento.type == pygame.QUIT:
            rodando = False

        if (
            evento.type == pygame.MOUSEBUTTONDOWN):  # Indica que haverá uma ação do tipo clique do botão do mouse
            
            # Inicia a animação da tacada
            tacando = True
            tempo_tacada = pygame.time.get_ticks()
            
            # Se estiver na tela inicial, o clique começa o jogo
            if estado_jogo == "INICIO":
                estado_jogo = "JOGANDO"
                fundo.fadeout(800)   # some em 0,8 segundo
                som_estadio.play(-1, fade_ms=1000)   # entra suavemente e repete
                som_bola_ar.play()

            # Se estiver jogando, o clique pode ser uma tacada
            elif estado_jogo == "JOGANDO":
                if bola_na_zona and not game_over and not bola_subindo:
                    # A bola foi rebatida
                    bola_rebatida = True
                    som_bola_ar.stop()   # corta o som da bola no ar
                    som_taco.play()
                    som_organ.play(maxtime=2100, fade_ms=0)
                    posicao_na_zona = max(0, min(1, (x_bola - x_zona) / largura_zona))

                    if posicao_na_zona >= LIMITE_PERFEITA:
                        tipo_tacada = "PERFEITA"
                    elif posicao_na_zona >= LIMITE_BOA:
                        tipo_tacada = "BOA"
                    else:
                        tipo_tacada = "FRACA"

                    cfg = TACADAS[tipo_tacada]
                    pontuacao += cfg["pontos"]

                    angulo_rad = math.radians(random.uniform(*cfg["desvio"]))
                    velocidade_x = -cfg["velocidade"] * math.cos(angulo_rad)
                    velocidade_y = random.choice([-1, 1]) * cfg["velocidade"] * math.sin(angulo_rad)

                    bola_subindo = True
                    x_maximo_bola = x_bola - cfg["distancia"]


        # ============================================================
        # DEFINICAO DA TECLA DE REINICIO DO JOGO
        # ============================================================
        if (
            evento.type == pygame.KEYDOWN
        ):  # Indica que o jogo irá ter uma tecla para pressionar que reiniciará o jogo
            if evento.key == pygame.K_F5:
                reiniciar_jogo()

    # ============================================================
    # ALTERAÇAO DA FASE DE ACORDO COM A PONTUACAO TOTAL
    # ============================================================
    
    if estado_jogo == "JOGANDO": # Só executa a lógica da bola durante a partida
        
       # Define a fase de acordo com a pontuação (máximo fase 5)
        fase = min(pontuacao // 500 + 1, 5)
        velocidade_descida = 2 + fase

        # ============================================================
        # MOVIMENTACAO DA BOLA
        # ============================================================
        if not game_over:

            x_bola = x_bola + velocidade_x
            y_bola = y_bola + velocidade_y

        # Verifica se a bola chegou ao limite da subida
        if bola_subindo and x_bola <= x_maximo_bola and tempo_bola_parada == 0:

            # Para a bola
            velocidade_x = 0
            velocidade_y = 0

            # Guarda o momento em que a bola parou
            tempo_bola_parada = pygame.time.get_ticks()


            # Verifica se a bola terminou sua subida
        if bola_subindo and velocidade_x == 0 and velocidade_y == 0:

            # Pega o tempo atual
            tempo_atual = pygame.time.get_ticks()

            # Espera 2 segundos antes de lançar a próxima bola
            if tempo_atual - tempo_bola_parada >= 2000:

            # Volta para a posição inicial
                x_bola = x_inicial_bola
                y_bola = y_pitch + altura_pitch // 2

            # Prepara uma nova descida
                velocidade_x = velocidade_descida
                velocidade_y = 0
                som_bola_ar.play()

            # Reseta os estados da bola
                bola_subindo = False
                bola_rebatida = False
                bola_na_zona = False
                tempo_bola_parada = 0

        # Verifica se a bola entrou na zona de rebatida
        if (
            x_bola >= x_zona
            and x_bola <= x_zona + largura_zona
            and not bola_na_zona
        ):
            bola_na_zona = True            
        # Verifica se a bola passou pelo jogador sem ser rebatida
        if x_bola > x_jogador and not game_over and not bola_rebatida:
            game_over = True
            estado_jogo = "GAME_OVER"
            pygame.mixer.stop()   # para todos os sons
            som_game_over.play()     # toca depois, para não ser cortado
            
            # Salva o recorde, se a pontuação atual for maior
            if pontuacao > recorde:
                recorde = pontuacao
                with open("recorde.txt", "w") as arquivo:
                    arquivo.write(str(recorde))
            
        # ------------------------------------------------------------
        # ANIMAÇÃO DA TACADA
        # ------------------------------------------------------------

        # Controla a animação da tacada
        if tacando:
            # Calcula quanto tempo já passou desde o início da tacada
            tempo_decorrido = pygame.time.get_ticks() - tempo_tacada

            # Primeira metade: o braço e o taco avançam
            if tempo_decorrido < duracao_tacada / 2:

            # Converte o tempo em um valor de 0 até 1
                progresso = tempo_decorrido / (duracao_tacada / 2)

            # Aumenta o ângulo gradualmente até 20 graus
                angulo_tacada = 20 * progresso

            # Segunda metade: o braço e o taco retornam
            else:

            # Calcula o progresso do retorno, de 0 até 1
                progresso = (tempo_decorrido - duracao_tacada / 2) / (duracao_tacada / 2)

            # Diminui o ângulo gradualmente até 0
                angulo_tacada = 20 * (1 - progresso)

            # Quando a animação termina, volta para a posição inicial
            if tempo_decorrido >= duracao_tacada:
                tacando = False
                angulo_tacada = 0
            
    # ============================================================
    # TELA
    # ============================================================
    tela.fill((110, 80, 55))

   # ============================================================
   # TELA DE INICIO
   # ============================================================

    # Tela inicial
    if estado_jogo == "INICIO":
        tela.blit(tela_inicial, (0, 0))
        desenhar_texto_contorno( "TACADA!",
            fonte_titulo,
            (255, 128, 0),
            (0, 0, 0),
            (230, 150)
    )
        desenhar_texto_contorno( "Quando a bola entrar na zona, clique para rebater!",
            fonte,
            (255, 128, 0),
            (0, 0, 0),
            (150, 240)
    )
        desenhar_texto_contorno( "Quanto mais perto do taco, melhor a tacada.",
            fonte_pequena,
            (255, 128, 0),
            (0, 0, 0),
            (190, 285)
    )
        desenhar_texto_contorno( "CLIQUE PARA COMEÇAR",
            fonte,
            (255, 128, 0),
            (0, 0, 0),
            (275, 400)
    )
   
    # ============================================================
    # ESTADO DO JOGO = JOGANDO
    # ============================================================
    if estado_jogo == "JOGANDO":
        tela.blit(
            arquibancada,
            (0, 0)
    )
    
        texto_pontos = fonte.render(
        f"PONTOS: {pontuacao}",
        True,
        (255, 255, 255)
        )

        tela.blit(texto_pontos, (20, 20))
        
        texto_tacada = fonte.render(
        f"Tacada: {tipo_tacada}",
        True,
        (255, 255, 255)
    )

        tela.blit(texto_tacada, (20, 55))
        
        # ============================================================
        # CENÁRIO
        # ============================================================
        
        tela.blit(cenario, (0, 0))
        # Pontuação e tipo da última tacada
        texto_pontos = fonte.render(f"PONTOS: {pontuacao}", True, (138, 19, 19))
        tela.blit(texto_pontos, (20, 20))

        texto_tacada = fonte.render(f"Tacada: {tipo_tacada}", True, (138, 19, 19))
        tela.blit(texto_tacada, (20, 55))

        ########### BOLA ##########
        tela.blit(
            bola_img,
        (
            x_bola - bola_img.get_width() // 2,
            y_bola - bola_img.get_height() // 2
        )   
    )

        
         
    ########### JOGADOR (corpo + braço + taco) ##########

    # --- Ajustes finos ---
        # --- Ajustes finos ---
        angulo_repouso_taco = -100
        amplitude_taco = 90
        angulo_repouso_braco = 6   # inclinação do braço: mão embaixo, ombro mais alto e atrás
        amplitude_braco = 4        # o braço acompanha pouco, para não soltar do ombro
        corpo_dx = 2                # antes 8: corpo bem encostado no ombro, só um pouco atrás
        corpo_dy = -8               # antes -4
        mao_dy = 9

    # Progresso da tacada: 0 (parado) até 1 (taco no ponto máximo)
        fator = angulo_tacada / 20
        angulo_taco = angulo_repouso_taco + amplitude_taco * fator
        angulo_braco = angulo_repouso_braco - amplitude_braco * fator

    # Mão: ponto fixo na linha da bola
        mao = pygame.math.Vector2(x_jogador, y_jogador + mao_dy)

     # Braço: pivô na ponta ESQUERDA (a mão), o resto se estende para trás da linha
        pivo_braco = (0, braco_pronto.get_height() // 2)
        pos_braco = mao

    # Ombro: ponta direita do braço
        ombro = pos_braco + pygame.math.Vector2(braco_pronto.get_width(), 0).rotate(-angulo_repouso_braco)

    # Corpo (desenhado primeiro, fica atrás)
        rect_corpo = personagem_pronto.get_rect(
            midtop=(ombro.x + corpo_dx, ombro.y + corpo_dy)
        )
        tela.blit(personagem_pronto, rect_corpo)

    # Braço (atrás do taco)
        blit_com_pivo(braco_pronto, pivo_braco, pos_braco, angulo_braco)

    # Taco: cabo na extremidade direita da imagem, preso à mão
        pivo_taco = (taco_pronto.get_width() - 3, taco_pronto.get_height() // 2)
        blit_com_pivo(taco_pronto, pivo_taco, mao, angulo_taco)
        
    # ============================================================
    # ESTADO DO JOGO = GAME OVER
    # ============================================================

    # Tela GAME OVER
    if estado_jogo == "GAME_OVER":
        tela.blit(tela_game_over, (0, 0))

        desenhar_texto_contorno( "A bola passou pelo jogador.",
            fonte,
            (255, 255, 0),  # Amarelo
            (0, 0, 0),      # Contorno preto
            (235, 210)
        )

        desenhar_texto_contorno(
            f"Pontuação final: {pontuacao}",
            fonte,
            (255, 255, 0),  # Amarelo
            (0, 0, 0),      # Contorno preto
            (270, 250)
        )
        desenhar_texto_contorno(
            f"Recorde: {recorde}",
            fonte,
            (255, 255, 0),
            (0, 0, 0),
            (270, 340)
        )

        desenhar_texto_contorno(
            "F5 - Jogar novamente",
            fonte,
            (255, 255, 0),  # Amarelo
            (0, 0, 0),      # Contorno preto
            (270, 300)
        )
        
        
    # ============================================================
    # ATUALIZAÇÃO DA TELA COM OS DESENHOS DEFINIDOS EM PYGAME.DRAW OU TELA.BLIT
    # ============================================================
    pygame.display.flip()  # Atualiza a tela com o que foi desenhado no draw.rect

    # ============================================================
    # LIMITAÇÃO DE FPS PARA MELHOR DESEMPENHO DE FUNCIONAMENTO
    # ============================================================
    clock.tick(60)  # Usamos o relógio para limitar o jogo a 60 FPS - isso impede que o jogo execute mais rápido do que a máquina consegue suportar

# ============================================================
# FECHAMENTO DO JOGO APÓS A FINALIZAÇÃO DO LOOP
# ============================================================
pygame.quit()
