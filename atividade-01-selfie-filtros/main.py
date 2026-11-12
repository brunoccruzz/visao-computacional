"""Atividade 01 - Selfie com nome/RA, flips e filtros de cor com OpenCV.

Uso:
    python main.py                          # tira a selfie pela câmera
    python main.py foto.jpg                 # usa uma foto já existente
    python main.py --nome "Fulano" --ra 123 # define o texto da imagem

Nome e RA também podem vir das variáveis de ambiente ALUNO_NOME e ALUNO_RA.
"""

import argparse
import os
from pathlib import Path

import cv2
import numpy as np

PASTA_SAIDA = Path(__file__).parent / "saida"
FONTE = cv2.FONT_HERSHEY_SIMPLEX
BRANCO = (255, 255, 255)
TECLA_ESPACO = 32
TECLA_ESC = 27


def dados_img(img):
    print(f"Largura em pixels: {img.shape[1]}")
    print(f"Altura em pixels: {img.shape[0]}")
    print(f"Quantidade de canais: {img.shape[2]}")


def tirar_selfie():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Não foi possível abrir a câmera")
        return None

    print("Pressione ESPAÇO para tirar a selfie.")
    print("Pressione ESC para sair.")

    selfie = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Não foi possível capturar a imagem")
            break

        cv2.imshow("Camera", frame)
        tecla = cv2.waitKey(1) & 0xFF

        if tecla == TECLA_ESPACO:
            selfie = frame.copy()
            break
        if tecla == TECLA_ESC:
            break

    cap.release()
    cv2.destroyAllWindows()
    return selfie


def salvar(nome_arquivo, img):
    caminho = PASTA_SAIDA / nome_arquivo
    cv2.imwrite(str(caminho), img)
    print(f"Salvo: {caminho}")


# ==================================================
# 1) SELFIE COM NOME E RA NO CANTO SUPERIOR DIREITO
# ==================================================
def escrever_nome_ra(img, nome, ra):
    img = img.copy()
    largura = img.shape[1]

    for i, texto in enumerate((nome, ra)):
        if not texto:
            continue
        tamanho = cv2.getTextSize(texto, FONTE, 0.7, 2)[0]
        posicao = (largura - tamanho[0] - 20, 30 + i * 30)
        cv2.putText(img, texto, posicao, FONTE, 0.7, BRANCO, 2, cv2.LINE_AA)

    return img


# ==================================================
# 2) ORIGINAL + 3 FLIPS EM UMA SÓ IMAGEM
# flipCode: 1 = horizontal, 0 = vertical, -1 = ambos
# ==================================================
def mosaico_flips(img):
    pequena = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2))

    linha_cima = np.hstack((pequena, cv2.flip(pequena, 1)))
    linha_baixo = np.hstack((cv2.flip(pequena, 0), cv2.flip(pequena, -1)))
    return np.vstack((linha_cima, linha_baixo))


# ==================================================
# 3) FILTROS R, G, B
# O OpenCV guarda em BGR: canal 0 = B, 1 = G, 2 = R
# Mantém só um canal e zera os outros dois
# ==================================================
def filtros_rgb(img):
    b, g, r = cv2.split(img)
    zeros = np.zeros_like(b)
    return {
        "R": cv2.merge([zeros, zeros, r]),
        "G": cv2.merge([zeros, g, zeros]),
        "B": cv2.merge([b, zeros, zeros]),
    }


# ==================================================
# 4) FILTROS GRAY, HSV E LAB
# ==================================================
def filtros_espacos_cor(img):
    return {
        "GRAY": cv2.cvtColor(img, cv2.COLOR_BGR2GRAY),
        "HSV": cv2.cvtColor(img, cv2.COLOR_BGR2HSV),
        "LAB": cv2.cvtColor(img, cv2.COLOR_BGR2LAB),
    }


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("imagem", nargs="?", help="foto existente (opcional)")
    parser.add_argument("--nome", default=os.getenv("ALUNO_NOME", ""))
    parser.add_argument("--ra", default=os.getenv("ALUNO_RA", ""))
    return parser.parse_args()


def main():
    args = parse_args()

    selfie = cv2.imread(args.imagem) if args.imagem else tirar_selfie()
    if selfie is None:
        print("Nenhuma imagem para processar")
        return

    PASTA_SAIDA.mkdir(exist_ok=True)
    dados_img(selfie)

    ra = f"RA: {args.ra}" if args.ra else ""
    selfie = escrever_nome_ra(selfie, args.nome, ra)

    resultados = {"Selfie": selfie, "Flips": mosaico_flips(selfie)}
    resultados.update(filtros_rgb(selfie))
    resultados.update(filtros_espacos_cor(selfie))

    arquivos = [
        "01_selfie_nome_ra.png", "02_flips_mosaico.png",
        "03_filtro_R.png", "04_filtro_G.png", "05_filtro_B.png",
        "06_filtro_GRAY.png", "07_filtro_HSV.png", "08_filtro_LAB.png",
    ]
    for arquivo, (titulo, img) in zip(arquivos, resultados.items()):
        salvar(arquivo, img)
        cv2.imshow(titulo, img)

    print("Pressione qualquer tecla para fechar.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
