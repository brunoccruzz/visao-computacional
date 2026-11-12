"""Atividade 02 - Detecção de bordas (Canny) e contagem de objetos.

Pipeline visto em aula:
    1. tons de cinza  2. blur  3. binarização (Otsu)  4. Canny  5. contornos externos

Uso:
    python bordas.py foto.jpg                      # parâmetros padrão (blur 7, canny 70/150)
    python bordas.py foto.jpg --blur 11 --canny 30 100
    python bordas.py --camera --nome selfie        # tira a foto pela webcam
    python bordas.py foto.jpg --comparar           # grade variando blur e canny
"""

import argparse
from pathlib import Path

import cv2
import mahotas
import numpy as np

PASTA_SAIDA = Path(__file__).parent / "saida"
LARGURA_MAX = 800

BLURS = (3, 7, 15)
CANNYS = ((30, 100), (70, 150), (150, 250))


def escreve(img, texto, cor=(255, 0, 0)):
    """Escreve no canto superior esquerdo com fundo para ficar legível."""
    fonte = cv2.FONT_HERSHEY_SIMPLEX
    (w, h), _ = cv2.getTextSize(texto, fonte, 0.6, 2)
    fundo = 0 if np.mean(cor) > 127 else 255
    if img.ndim == 3:
        fundo = (fundo, fundo, fundo)
    cv2.rectangle(img, (0, 0), (w + 20, h + 16), fundo, -1)
    cv2.putText(img, texto, (10, h + 8), fonte, 0.6, cor, 2, cv2.LINE_AA)


def redimensionar(img, largura_max=LARGURA_MAX):
    if img.shape[1] <= largura_max:
        return img
    escala = largura_max / img.shape[1]
    return cv2.resize(img, None, fx=escala, fy=escala, interpolation=cv2.INTER_AREA)


def tirar_foto():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Não foi possível abrir a câmera")
        return None

    print("ESPAÇO tira a foto, ESC sai.")
    foto = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Camera", frame)
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == 32:
            foto = frame.copy()
            break
        if tecla == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return foto


def processar(img_colorida, blur=7, limiar1=70, limiar2=150):
    """Roda o pipeline e devolve as etapas e os contornos encontrados."""
    # Passo 1: tons de cinza
    cinza = cv2.cvtColor(img_colorida, cv2.COLOR_BGR2GRAY)

    # Passo 2: blur / suavização
    suave = cv2.blur(cinza, (blur, blur))

    # Passo 3: binarização com Otsu (pixels só brancos e pretos)
    T = mahotas.thresholding.otsu(suave)
    binaria = suave.copy()
    binaria[binaria > T] = 255
    binaria[binaria < 255] = 0
    binaria = cv2.bitwise_not(binaria)

    # Passo 4: Canny
    bordas = cv2.Canny(binaria, limiar1, limiar2)

    # Passo 5: contornos externos
    objetos, _ = cv2.findContours(bordas.copy(), cv2.RETR_EXTERNAL,
                                  cv2.CHAIN_APPROX_SIMPLE)

    return {"cinza": cinza, "suave": suave, "binaria": binaria,
            "bordas": bordas, "objetos": objetos}


def desenhar_resultado(img_colorida, objetos, legenda=None):
    resultado = img_colorida.copy()
    cv2.drawContours(resultado, objetos, -1, (255, 0, 0), 2)
    escreve(resultado, legenda or f"{len(objetos)} objetos encontrados!")
    return resultado


def montar_etapas(etapas):
    cinza = etapas["cinza"].copy()
    suave = etapas["suave"].copy()
    binaria = etapas["binaria"].copy()
    bordas = etapas["bordas"].copy()

    escreve(cinza, "Imagem em tons de cinza", 0)
    escreve(suave, "Suavizacao com Blur", 0)
    escreve(binaria, "Binarizacao com Metodo Otsu", 255)
    escreve(bordas, "Detector de bordas Canny", 255)

    return np.vstack([np.hstack([cinza, suave]), np.hstack([binaria, bordas])])


def comparar(img_colorida):
    """Grade 3x3: linhas variam o blur, colunas variam os limiares do Canny."""
    linhas = []
    print(f"\n{'blur':>6} | {'canny':>9} | objetos")
    print("-" * 30)
    for blur in BLURS:
        celulas = []
        for l1, l2 in CANNYS:
            etapas = processar(img_colorida, blur, l1, l2)
            n = len(etapas["objetos"])
            print(f"{blur:>6} | {l1:>4}/{l2:<4} | {n}")
            celula = img_colorida.copy()
            cv2.drawContours(celula, etapas["objetos"], -1, (255, 0, 0), 2)
            celula = redimensionar(celula, LARGURA_MAX // 2)
            escreve(celula, f"blur {blur} | canny {l1}/{l2} | {n} obj")
            celulas.append(celula)
        linhas.append(np.hstack(celulas))
    return np.vstack(linhas)


def comparar_canny_sem_binarizar(img_colorida):
    """Canny direto na imagem suavizada (sem Otsu), para ver o efeito real
    dos limiares: na imagem binária todo degrau é 0->255 e passa em qualquer limiar."""
    cinza = cv2.cvtColor(img_colorida, cv2.COLOR_BGR2GRAY)
    linhas = []
    for blur in BLURS:
        suave = cv2.blur(cinza, (blur, blur))
        celulas = []
        for l1, l2 in CANNYS:
            bordas = redimensionar(cv2.Canny(suave, l1, l2), LARGURA_MAX // 2)
            escreve(bordas, f"blur {blur} | canny {l1}/{l2}", 255)
            celulas.append(bordas)
        linhas.append(np.hstack(celulas))
    return np.vstack(linhas)


def salvar(nome, img):
    caminho = PASTA_SAIDA / nome
    cv2.imwrite(str(caminho), img)
    print(f"Salvo: {caminho}")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("imagem", nargs="?", help="caminho da foto")
    p.add_argument("--camera", action="store_true", help="tira a foto pela webcam")
    p.add_argument("--nome", help="prefixo dos arquivos de saída")
    p.add_argument("--blur", type=int, default=7, help="tamanho do kernel do blur")
    p.add_argument("--canny", type=int, nargs=2, default=(70, 150),
                   metavar=("LIMIAR1", "LIMIAR2"))
    p.add_argument("--comparar", action="store_true",
                   help="gera grade variando blur e canny")
    p.add_argument("--sem-janela", action="store_true",
                   help="só salva os arquivos, sem abrir janelas")
    return p.parse_args()


def main():
    args = parse_args()

    if args.camera:
        img = tirar_foto()
    elif args.imagem:
        img = cv2.imread(args.imagem)
    else:
        print("Informe uma imagem ou use --camera")
        return

    if img is None:
        print("Nenhuma imagem para processar")
        return

    img = redimensionar(img)
    nome = args.nome or (Path(args.imagem).stem if args.imagem else "camera")
    PASTA_SAIDA.mkdir(exist_ok=True)

    if args.camera:
        salvar(f"{nome}_original.jpg", img)

    l1, l2 = args.canny
    etapas = processar(img, args.blur, l1, l2)
    n = len(etapas["objetos"])
    print(f"blur={args.blur} canny={l1}/{l2}: {n} objetos encontrados")

    sufixo = f"blur{args.blur}_canny{l1}-{l2}"
    janelas = {
        f"Etapas - {n} objetos": montar_etapas(etapas),
        "Resultado": desenhar_resultado(img, etapas["objetos"]),
    }
    salvar(f"{nome}_etapas_{sufixo}.jpg", janelas[f"Etapas - {n} objetos"])
    salvar(f"{nome}_resultado_{sufixo}.jpg", janelas["Resultado"])

    if args.comparar:
        janelas["Comparacao"] = comparar(img)
        salvar(f"{nome}_comparacao.jpg", janelas["Comparacao"])
        janelas["Canny sem binarizar"] = comparar_canny_sem_binarizar(img)
        salvar(f"{nome}_canny_sem_binarizar.jpg", janelas["Canny sem binarizar"])

    if not args.sem_janela:
        for titulo, imagem in janelas.items():
            cv2.imshow(titulo, imagem)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
