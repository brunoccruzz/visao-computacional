# Atividade 01 — Selfie e filtros de cor

Tira uma selfie pela webcam (ou usa uma foto existente) e gera:

1. **Selfie com nome e RA** escritos no canto superior direito
2. **Mosaico de flips** — original, horizontal, vertical e ambos numa só imagem
3. **Filtros R, G e B** — mantém um canal e zera os outros (lembrando que o OpenCV usa BGR)
4. **Espaços de cor** — GRAY, HSV e LAB

## Uso

```bash
python main.py                                  # câmera: ESPAÇO tira a foto, ESC sai
python main.py foto.jpg                         # usa uma foto existente
python main.py --nome "Seu Nome" --ra 12345678  # texto escrito na selfie
```

Nome e RA também podem ser definidos pelas variáveis de ambiente `ALUNO_NOME` e `ALUNO_RA`.

As imagens são salvas em `saida/` (ignorada pelo git):

```
01_selfie_nome_ra.png   05_filtro_B.png
02_flips_mosaico.png    06_filtro_GRAY.png
03_filtro_R.png         07_filtro_HSV.png
04_filtro_G.png         08_filtro_LAB.png
```
